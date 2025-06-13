import pandas as pd
from class_definition import *


def get_data_from_xlsx(self):
    # 공정 리스트
    self.df_process = pd.read_excel(self.config['data_file_path'], skiprows=[0, 1, 2], usecols='C:D', nrows=64)
    self.df_vehicle = pd.read_excel(self.config['data_file_path'], skiprows=[0, 1, 2, 3], usecols='F:BG', nrows=62)
    self.df_process = self.df_process.drop(index=self.df_process.index[0])
    self.df_process = self.df_process.reset_index(drop=True)
    self.df_process = self.df_process.map(lambda x: x.strip() if isinstance(x, str) else x)
    self.df_process = self.df_process.ffill()
    self.df_vehicle.index = self.df_process['세부공정명'].tolist()
    self.df_process.drop_duplicates(inplace=True)
    self.df_process = self.df_process.reset_index(drop=True)

    self.process_list = list(self.df_process['세부공정명'])
    self.operation_list = ["operation" + str(i) for i in range(len(self.process_list))]
    self.test_operation_list = [1, 8, 9, 10, 13, 19, 29, 33, 34, 36, 37, 42, 44, 47]
    self.TC_operation_list = [14, 20, 23, 26, 30, 32]
    self.operation_dict = {"operation" + str(i): Operation(row['세부공정명'], i, i in self.test_operation_list,
                                                           i in self.TC_operation_list, row['담당공정'][:2])
                           for i, row in self.df_process.iterrows()}
    self.same_sequence_constraint = [[1, 2], [38, 39, 40, 41], [42, 43], [46, 47]]

    self.calendar = Calendar()
    self.calendar.holiday = [1, 5, 12, 19, 26, 28, 29, 30]
    self.calendar.saturday = [4, 11, 18, 25]
    self.calendar.index_to_day_calendar_dict = {i: pd.to_datetime('2025-01-01') + pd.Timedelta(days=day - 1)
                                                for i, day in enumerate(range(self.start_time_index + 1,
                                                                                         self.end_time_index + 1))}
                                                # for i, day in enumerate(d for d in range(self.start_time_index + 1,
                                                #                                          self.end_time_index + 1)
                                                #                         if d not in self.calendar.holiday)}
    self.calendar.day_to_index_calendar_dict = \
        {value: key for key, value in self.calendar.index_to_day_calendar_dict.items()}

    columns = self.df_vehicle.columns.tolist()
    for i in range(1, len(columns)):  # 첫 번째 열은 처리할 필요 없음
        if isinstance(columns[i], str) and "Unnamed" in columns[i]:
            columns[i] = columns[i - 1]  # 바로 왼쪽 열 이름으로 대체
    self.df_vehicle.columns = columns

    for row_idx in range(self.df_vehicle.shape[0]):
        operation_name = self.df_vehicle.index[row_idx]
        for col_idx in range(self.df_vehicle.shape[1]):
            date = self.df_vehicle.columns[col_idx]
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
        print(vehicle_name, min_operation_index, self.vehicle_dict[vehicle_name].operation_dict[self.operation_list[min_operation_index]])
