import json
import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


def post_api(self, url, output_dict):
    url = 'https://corners.synology.me:30006/woojin-dev490/' + url
    # 요청 보내기
    response = requests.post(url, json=output_dict,
                             auth=HTTPBasicAuth(self.config['API_ID'], self.config['API_PASSWORD']), verify=False)

    # 응답 확인
    if response.status_code == 200:
        print(f'접근 성공: 상태 코드 {response.status_code}')
    else:
        print(f'접근 실패: 상태 코드 {response.status_code} / 메세지 {response.text}')


class Vehicles_result:
    def __init__(self, vehicle_name, type_TC):
        self.vehicle_name = vehicle_name
        self.type_TC = type_TC
        self.operation_list = list()
        self.operation_dict = dict()

    def add_operation(self, operation, date):
        if operation not in self.operation_dict:
            self.operation_dict[operation] = date


def save_results(self):
    if self.solution:
        print(self.solution.get_value(self.max_load))
        print(self.solution.get_value(self.min_load))
        for (vehicle_name, operation), var in self.operation_var_dict_by_vehicle_operation_dict.items():
            self.vehicle_dict[vehicle_name].operation_dict[operation] = self.solution.get_var_solution(var).get_start()
        for vehicle_name, vehicle in self.vehicle_dict.items():
            vehicle.operation_dict = dict(sorted(vehicle.operation_dict.items(), key=lambda item: item[1]))
            vehicle.operation_list = list(vehicle.operation_dict.keys())

        for_json = {
            "calendar": {
                "length": len(self.calendar.index_to_day_calendar_dict),
                "data": {
                    "holiday": self.calendar.holiday,
                    "saturday": self.calendar.saturday,
                    "index_to_day_calendar": {key: value.strftime('%Y-%m-%d') for key, value in
                                              self.calendar.index_to_day_calendar_dict.items()},
                    "day_to_index_calendar": {key.strftime('%Y-%m-%d'): value for key, value in
                                              self.calendar.day_to_index_calendar_dict.items()}
                }
            },
            "operations": {
                "num_items": len(self.operation_list),
                "data": {key: value.__dict__ for key, value in self.operation_dict.items()}
            },
            "vehicles": {
                "num_items": len(self.vehicle_dict),
                "data": {key: value.__dict__ for key, value in self.vehicle_dict.items()}
            }
        }

        file_path = self.config['folderpath'] + '/schedule_optimization_output.json'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # for_json_final 객체를 f 파일 스트림에 JSON 형식으로 씁니다.
                # ensure_ascii=False: 비 ASCII 문자(예: 한글)가 유니코드 이스케이프 없이 그대로 저장되도록 합니다.
                # indent=4: JSON 파일을 사람이 읽기 쉽게 4칸 들여쓰기로 형식화합니다.
                json.dump(for_json, f, ensure_ascii=False, indent=4)
            print(f"JSON 데이터가 '{file_path}' 파일로 성공적으로 저장되었습니다.")
            if self.config['output_save_API']:
                post_api(self, 'SNU/result', [for_json])
        except IOError as e:
            print(f"파일 저장 중 오류가 발생했습니다: {e}")
        except TypeError as e:
            # json.dump가 직렬화할 수 없는 객체를 만났을 때 발생 (예: __dict__로 처리 안 된 사용자 객체)
            print(f"JSON 직렬화 중 오류가 발생했습니다: {e}")

        results = []
        days = {'공정명': None, '담당공정': None, '검사공정여부': None, 'TC대상공정여부': None}
        for i in list(self.calendar.index_to_day_calendar_dict.keys()):
            days[i] = None
        for holiday in self.calendar.holiday:
            days[holiday] = 'holiday'
        for saturday in self.calendar.saturday:
            days[saturday] = 'saturday'
        results.append(days)
        counts = {'공정명': None, '담당공정': None, '검사공정여부': None, 'TC대상공정여부': None}
        for i in list(self.calendar.index_to_day_calendar_dict.keys()):
            counts[i] = 0
        for operation_name, operation in self.operation_dict.items():
            result = {'공정명': operation.operation_name, '담당공정': operation.department,
                      '검사공정여부': operation.test_operation, 'TC대상공정여부': operation.type_TC}
            for i in list(self.calendar.index_to_day_calendar_dict.keys()):
                result[i] = ' '
            for (vehicle_name, operation_name2), var in self.operation_var_dict_by_vehicle_operation_dict.items():
                if operation_name == operation_name2:
                    index = self.solution.get_var_solution(var).get_start()
                    if result[index] == ' ':
                        result[index] = vehicle_name
                    else:
                        result[index] += ', ' + vehicle_name
                    counts[index] += 1
            results.append(result)
        results.append(counts)
        result_df = pd.DataFrame(results,
                                 columns=['공정명', '담당공정', '검사공정여부', 'TC대상공정여부'] +
                                         list(self.calendar.index_to_day_calendar_dict.keys()))
        result_df.to_excel(self.config['folderpath'] + '/result_table.xlsx', index=False)

        # ## holiday를 제거하고 계산하도록 수정
        print('입력 시 일별 부하:', list(self.load_step_dict.values()))
        print('입력 시 부하 평균:', np.round(np.mean([value for key, value in self.load_step_dict.items() if key not in self.calendar.holiday]), 3))
        print('입력 시 부하 분산:', np.round(np.var([value for key, value in self.load_step_dict.items() if key not in self.calendar.holiday]), 3))
        print('-------------------------------------------------------')
        del counts['공정명']
        del counts['담당공정']
        del counts['검사공정여부']
        del counts['TC대상공정여부']
        print('최적화 결과 일별 부하:', list(counts.values()))
        print('최적화 결과 부하 평균:', np.round(np.mean([value for key, value in counts.items() if key not in self.calendar.holiday]), 3))
        print('최적화 결과 부하 분산:', np.round(np.var([value for key, value in counts.items() if key not in self.calendar.holiday]), 3))

        # print('입력 시 일별 부하:', list(self.load_step_dict.values()))
        # print('입력 시 부하 평균:', np.round(np.mean([value for value in self.load_step_dict.values()]), 3))
        # print('입력 시 부하 분산:', np.round(np.var([value for value in self.load_step_dict.values()]), 3))
        # print('-------------------------------------------------------')
        # del counts['공정명']
        # del counts['담당공정']
        # del counts['검사공정여부']
        # del counts['TC대상공정여부']
        # print('최적화 결과 일별 부하:', list(counts.values()))
        # print('최적화 결과 부하 평균:', np.round(np.mean([value for value in counts.values()]), 3))
        # print('최적화 결과 부하 분산:', np.round(np.var([value for value in counts.values()]), 3))
