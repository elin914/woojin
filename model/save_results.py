import json
import pandas as pd


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
                    "index_to_day_calendar": {key: value.strftime('%Y-%m-%d') for key, value in self.calendar.index_to_day_calendar_dict.items()},
                    "day_to_index_calendar": {key.strftime('%Y-%m-%d'): value for key, value in self.calendar.day_to_index_calendar_dict.items()}
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
        except IOError as e:
            print(f"파일 저장 중 오류가 발생했습니다: {e}")
        except TypeError as e:
            # json.dump가 직렬화할 수 없는 객체를 만났을 때 발생 (예: __dict__로 처리 안 된 사용자 객체)
            print(f"JSON 직렬화 중 오류가 발생했습니다: {e}")
