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
        print(f'접근 실패: 상태 코드 {response.status_code}')
        return False
    return data


def get_data_from_api(self):
    self.df_process = pd.DataFrame(load_api(self, 'Processes/Seq')['data'])
    self.df_process = self.df_process[(self.df_process['pcCd'] == 'PROC0004') | (self.df_process['pcCd'] == 'PROC0005')]

    row_temp = self.df_process[self.df_process['pcId'] == 'cfae0823-3d36-4f38-a902-619beca12b22']
    self.df_process = self.df_process[self.df_process['pcId'] != 'cfae0823-3d36-4f38-a902-619beca12b22']
    self.df_process = pd.concat([self.df_process, row_temp]).reset_index(drop=True)
    self.process_list = list(self.df_process['pcNm'])
    self.operation_dict = {"operation" + str(i): Operation(row['pcNm'], row['pcId'], i,
                                                           row['examCheck'], row['tcCheck'], row['pcTp'])
                           for i, row in self.df_process.iterrows()}
    self.operation_list = list(self.operation_dict)
    self.operation_id_to_key_dict = {value.id: key for key, value in self.operation_dict.items()}
    self.same_sequence_constraint = [[9, 10], [21, 22], [24, 25], [26, 27], [39, 40, 41],
                                     [42, 43], [44, 45, 46, 47], [48, 49, 50]]

    self.calendar = Calendar()
    date_range = list(pd.date_range(start=self.start_time, end=self.end_time, freq='D'))
    self.calendar.index_to_day_calendar_dict = {i: date for i, date in enumerate(date_range)}
    self.calendar.day_to_index_calendar_dict = \
        {value: key for key, value in self.calendar.index_to_day_calendar_dict.items()}
    self.calendar.saturday = [index for index, date in enumerate(date_range) if date.weekday() == 5]
    self.calendar.holiday = [index for index, date in enumerate(date_range) if date.weekday() == 6]
    self.end_time_index = max(self.calendar.index_to_day_calendar_dict.keys())

    self.df_vehicle = pd.DataFrame(load_api(self, 'Cars/' + self.config['project_id'] + '?allYn=Y')['data'])
    for i, row in self.df_vehicle.iterrows():
        data_temp = load_api(self, 'WorkPlan/' + self.config['project_id'] + '/' + row['carId'])
        if data_temp['code'] == 10:
            continue
        df_temp = pd.DataFrame(data_temp['data'])
        df_temp = df_temp[pd.to_datetime(df_temp['planDate']) >= self.start_time]
        df_temp = df_temp[pd.to_datetime(df_temp['planDate']) <= self.end_time]
        df_temp = df_temp[df_temp['pcId'].isin(self.df_process['pcId'])]
        if df_temp.shape[0] == 0:
            continue
        self.vehicle_dict[row['carCd']] = Vehicle(row['carCd'], row['carId'], int(row['carSeq']), 'TC' in row['carType'])
        for _, row2 in df_temp.iterrows():
            self.vehicle_dict[row['carCd']].add_operation(self.operation_id_to_key_dict[row2['pcId']],
                                                          self.calendar.day_to_index_calendar_dict[pd.to_datetime(row2['planDate'])])
            if self.operation_id_to_key_dict[row2['pcId']] == 'operation2':
                self.operation0_dict[row['carCd']] = self.calendar.day_to_index_calendar_dict[pd.to_datetime(row2['planDate'])]
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation in vehicle.operation_dict:
            vehicle.operation_list.append(operation)

    self.load_step_dict = {index: 0 for index in self.calendar.index_to_day_calendar_dict}
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation_name, date in vehicle.operation_dict.items():
            self.load_step_dict[date] += 1
    print(self.load_step_dict)


def get_data_from_xlsx(self):
    # # 공정 리스트
    # self.df_process = pd.read_excel(self.config['data_file_path1'], skiprows=[0, 1, 2], usecols='C:D', nrows=64)
    # df_vehicle1 = pd.read_excel(self.config['data_file_path1'], skiprows=[0, 1, 2, 3], usecols='F:BG', nrows=62)
    # df_vehicle2 = pd.read_excel(self.config['data_file_path2'], skiprows=[0, 1, 2, 3], usecols='F:BA', nrows=62)
    # df_vehicle3 = pd.read_excel(self.config['data_file_path3'], skiprows=[0, 1, 2, 3], usecols='F:BE', nrows=62)
    self.df_process = pd.read_excel(self.config['data_file_path1'], skiprows=[0, 1, 2, 5, 6, 7], usecols='C:D', nrows=61)
    df_vehicle1 = pd.read_excel(self.config['data_file_path1'], skiprows=[0, 1, 2, 3, 5, 6, 7], usecols='F:BG', nrows=59)
    df_vehicle2 = pd.read_excel(self.config['data_file_path2'], skiprows=[0, 1, 2, 3, 5, 6, 7], usecols='F:BA', nrows=59)
    df_vehicle3 = pd.read_excel(self.config['data_file_path3'], skiprows=[0, 1, 2, 3, 5, 6, 7], usecols='F:BE', nrows=59)
    self.df_process = self.df_process.drop(index=self.df_process.index[0])
    self.df_process = self.df_process.reset_index(drop=True)
    self.df_process = self.df_process.map(lambda x: x.strip() if isinstance(x, str) else x)
    self.df_process = self.df_process.ffill()
    df_vehicle1.index = self.df_process['세부공정명'].tolist()
    df_vehicle2.index = self.df_process['세부공정명'].tolist()
    df_vehicle3.index = self.df_process['세부공정명'].tolist()
    self.df_process.drop_duplicates(inplace=True)
    self.df_process = self.df_process.reset_index(drop=True)

    self.process_list = list(self.df_process['세부공정명'])
    self.operation_list = ["operation" + str(i) for i in range(len(self.process_list))]
    # self.test_operation_list = [1, 8, 9, 10, 13, 19, 29, 33, 34, 36, 37, 42, 44, 47]
    self.test_operation_list = [0, 5, 6, 7, 10, 16, 26, 30, 31, 33, 34, 39, 41, 44]  # 제약 만족을 위해 수정
    # self.TC_operation_list = [14, 20, 23, 26, 30, 32]
    self.TC_operation_list = [11, 17, 20, 23, 27, 29]
    self.operation_dict = {"operation" + str(i): Operation(row['세부공정명'], i, i in self.test_operation_list,
                                                           i in self.TC_operation_list, row['담당공정'][:2])
                           for i, row in self.df_process.iterrows()}
    # self.same_sequence_constraint = [[1, 2], [38, 39, 40, 41], [42, 43], [46, 47]]
    self.same_sequence_constraint = [[35, 36, 37, 38], [39, 40], [43, 44]]

    self.calendar = Calendar()
    # self.calendar.holiday = [0, 4, 11, 18, 25, 27, 28, 29]
    self.calendar.holiday = [0, 4, 11, 18, 25, 27, 28, 29, 32, 39, 46, 53, 59, 60, 61, 67, 74, 81, 88]
    # self.calendar.saturday = [3, 10, 17, 24]
    self.calendar.saturday = [3, 10, 17, 24, 31, 38, 45, 52, 66, 73, 80, 87]
    self.calendar.index_to_day_calendar_dict = {i: pd.to_datetime('2025-01-01') + pd.Timedelta(days=day - 1)
                                                for i, day in enumerate(range(self.start_time_index + 1,
                                                                                         self.end_time_index + 1))}
                                                # for i, day in enumerate(d for d in range(self.start_time_index + 1,
                                                #                                          self.end_time_index + 1)
                                                #                         if d not in self.calendar.holiday)}
    self.calendar.day_to_index_calendar_dict = \
        {value: key for key, value in self.calendar.index_to_day_calendar_dict.items()}

    columns = df_vehicle1.columns.tolist()
    for i in range(len(columns)):
        if isinstance(columns[i], str) and "Unnamed" in columns[i]:
            columns[i] = columns[i - 1]  # 바로 왼쪽 열 이름으로 대체
    df_vehicle1.columns = columns

    columns = df_vehicle2.columns.tolist()
    for i in range(len(columns)):
        if isinstance(columns[i], int):
            columns[i] = columns[i] + 31
        elif isinstance(columns[i], str) and "Unnamed" in columns[i]:
            columns[i] = columns[i - 1]  # 바로 왼쪽 열 이름으로 대체
    df_vehicle2.columns = columns

    columns = df_vehicle3.columns.tolist()
    for i in range(len(columns)):
        if isinstance(columns[i], int):
            columns[i] = columns[i] + 59
        elif isinstance(columns[i], str) and "Unnamed" in columns[i]:
            columns[i] = columns[i - 1]  # 바로 왼쪽 열 이름으로 대체
    df_vehicle3.columns = columns

    self.df_vehicle = pd.concat([df_vehicle1, df_vehicle2, df_vehicle3], axis=1)

    for row_idx in range(self.df_vehicle.shape[0]):
        operation_name = self.df_vehicle.index[row_idx]
        for col_idx in range(self.df_vehicle.shape[1]):
            date = self.df_vehicle.columns[col_idx] - 1
            vehicle_name = self.df_vehicle.iloc[row_idx, col_idx]

            if pd.notna(vehicle_name):
                if vehicle_name not in self.vehicle_dict:
                    self.vehicle_dict[vehicle_name] = Vehicle(vehicle_name, 'TC' in vehicle_name)
                self.vehicle_dict[vehicle_name].add_operation(
                    self.operation_list[self.process_list.index(operation_name)], date)

    vehicle_order_dict = dict()
    for vehicle_name, vehicle in self.vehicle_dict.items():
        if 'operation0' in vehicle.operation_dict:
            self.operation0_dict[vehicle_name] = vehicle.operation_dict['operation0']
        min_operation_index = len(self.operation_list)
        for operation in vehicle.operation_dict:
            # self.operation_dict[operation].left_vehicle_list.append(vehicle_name)
            vehicle.operation_list.append(operation)
            min_operation_index = min(self.operation_list.index(operation), min_operation_index)
        vehicle_order_dict[vehicle_name] = min_operation_index

    sorted_list = sorted(vehicle_order_dict.items(), key=lambda item: (-item[1], self.vehicle_dict[item[0]].operation_dict[self.operation_list[item[1]]]))
    for i, (vehicle_name, min_operation_index) in enumerate(sorted_list):
        self.vehicle_dict[vehicle_name].order = i
        # print(vehicle_name, min_operation_index, self.vehicle_dict[vehicle_name].operation_dict[self.operation_list[min_operation_index]])

    self.load_step_dict = {index: 0 for index in self.calendar.index_to_day_calendar_dict}
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation_name, date in vehicle.operation_dict.items():
            self.load_step_dict[date] += 1
    print(self.load_step_dict)
