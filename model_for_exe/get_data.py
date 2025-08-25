import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import json
from class_definition import *
# 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_api(self, url, save_data=False):
    url = 'https://corners.synology.me:30006/woojin-dev490/' + url
    # 요청 보내기
    response = requests.get(url, auth=HTTPBasicAuth(self.config['API_ID'], self.config['API_PASSWORD']), verify=False)

    # 응답 확인
    if response.status_code == 200:
        data = response.json()  # JSON 형식으로 파싱
        if save_data:
            # JSON 파일로 저장
            with open('output.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print(f'접근 실패: 상태 코드 {response.status_code} / 메세지 {response.text}')
        return False
    return data


def get_data_from_api(self):
    self.df_process = pd.DataFrame(load_api(self, 'Processes/Seq')['data'])
    self.df_process = self.df_process[(self.df_process['pcCd'] == 'PROC0004') | (self.df_process['pcCd'] == 'PROC0005')]

    row_temp = self.df_process[self.df_process['pcId'] == 'cfae0823-3d36-4f38-a902-619beca12b22']
    self.df_process = self.df_process[self.df_process['pcId'] != 'cfae0823-3d36-4f38-a902-619beca12b22']
    self.df_process = pd.concat([self.df_process, row_temp]).reset_index(drop=True)
    self.process_list = list(self.df_process['pcNm'])
    self.operation_dict = {"operation" + str(i): Operation(row['pcNm'], row['pcId'], i, row['examCheck'],
                                                           row['tcCheck'], row['pcTp'] if not row['examCheck'] else 0)
                           for i, row in self.df_process.iterrows()}
    self.operation_list = list(self.operation_dict)
    self.operation_id_to_key_dict = {value.id: key for key, value in self.operation_dict.items()}
    self.same_sequence_constraint = [[9, 10], [21, 22], [24, 25], [26, 27], [39, 40, 41],
                                     [42, 43], [44, 45, 46, 47], [48, 49, 50]]
    print("Load Operation Completed")

    self.calendar = Calendar()
    date_range = list(pd.date_range(start=self.start_time, end=self.end_time, freq='D'))
    self.calendar.index_to_day_calendar_dict = {i: date for i, date in enumerate(date_range)}
    self.calendar.day_to_index_calendar_dict = \
        {value: key for key, value in self.calendar.index_to_day_calendar_dict.items()}
    self.calendar.saturday = [index for index, date in enumerate(date_range) if date.weekday() == 5]
    self.calendar.holiday = [index for index, date in enumerate(date_range) if date.weekday() == 6]
    # df_holiday = pd.DataFrame(load_api(self, 'Holiday')['data'])
    # df_holiday['offDate'] = pd.to_datetime(df_holiday['offDate'])
    # df_holiday = df_holiday[(self.start_time <= df_holiday['offDate']) & (df_holiday['offDate'] <= self.end_time)]
    # for holiday in list(df_holiday['offDate']):
    #     self.calendar.holiday.append(self.calendar.day_to_index_calendar_dict[holiday])
    # self.calendar.holiday = sorted(self.calendar.holiday)
    self.end_time_index = max(self.calendar.index_to_day_calendar_dict.keys())
    print("Load calendar Completed")

    df_vehicle = pd.DataFrame(load_api(self, 'Cars/' + self.config['project_id'] + '?allYn=Y')['data'])
    df_har = pd.DataFrame(load_api(self, 'WorkPlan/harness/' + self.config['project_id'])['data'])
    df_har['planDate'] = pd.to_datetime(df_har['planDate'])
    df_har = df_har.loc[df_har.groupby('carId')['planDate'].idxmin()]
    df_har['harnessSeq'] = df_har['planDate'].rank(method='dense').astype(int)
    self.df_vehicle = pd.merge(df_vehicle, df_har, on='carId', how='left').fillna(0)
    self.df_vehicle['harnessSeq'] = self.df_vehicle['harnessSeq'].astype(int)
    # self.df_vehicle = self.df_vehicle[self.df_vehicle['harnessSeq'] != 0]
    for i, row in self.df_vehicle.iterrows():
        data_temp = load_api(self, 'WorkPlan/' + self.config['project_id'] + '?carId=' + row['carId'])
        if data_temp['code'] == 10:
            continue
        df_temp = pd.DataFrame(data_temp['data'])
        df_temp = df_temp[pd.to_datetime(df_temp['planDate']) >= self.start_time]
        df_temp = df_temp[pd.to_datetime(df_temp['planDate']) <= self.end_time]
        df_temp = df_temp[df_temp['pcId'].isin(self.df_process['pcId'])]
        if df_temp.shape[0] == 0:
            continue
        self.vehicle_dict[row['carCd']] = Vehicle(row['carCd'], row['carId'], int(row['harnessSeq']), 'TC' in row['carType'])
        for _, row2 in df_temp.iterrows():
            self.vehicle_dict[row['carCd']].add_operation(self.operation_id_to_key_dict[row2['pcId']],
                                                          self.calendar.day_to_index_calendar_dict[pd.to_datetime(row2['planDate'])])
            if self.operation_id_to_key_dict[row2['pcId']] == 'operation2' and row['carCd'] not in self.operation0_dict:
                self.operation0_dict[row['carCd']] = self.calendar.day_to_index_calendar_dict[pd.to_datetime(row2['planDate'])]
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation in vehicle.operation_dict:
            vehicle.operation_list.append(operation)
        vehicle.operation_dict = {key: vehicle.operation_dict[key] for key in sorted([key for key in vehicle.operation_dict.keys()], key=lambda x: int(x.replace('operation', '')))}
        vehicle.min_operation_name = min(vehicle.operation_dict, key=vehicle.operation_dict.get)
    print("Load Vehicle Completed")

    self.load_step_dict = {index: 0 for index in self.calendar.index_to_day_calendar_dict}
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation_name, date in vehicle.operation_dict.items():
            self.load_step_dict[date] += 1
    print(self.load_step_dict)
    for date in [key for key, value in self.load_step_dict.items() if value == 0]:
        if date not in self.calendar.holiday:
            self.calendar.holiday.append(date)
    self.calendar.holiday = sorted(self.calendar.holiday)
