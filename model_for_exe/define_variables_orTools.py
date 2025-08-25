def define_variables(self):
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation_name in vehicle.operation_list:
            duration = 1

            #intVariable 정의
            start_var = self.model.NewIntVar(self.start_time_index, self.end_time_index, f"start_var[{vehicle_name},{operation_name}]")
            end_var = self.model.NewIntVar(self.start_time_index + duration, self.end_time_index + duration, f"end_var[{vehicle_name},{operation_name}]")
            # intervalVariable 정의
            int_var = self.model.NewIntervalVar(start_var, duration, end_var, f"int_var[{vehicle_name},{operation_name}]")

            # 추후 제약에서 사용하기 위해 self. starts, ends, intervals를 별도로 indexing 해 둠
            self.starts[(vehicle_name, operation_name)] = start_var
            self.ends[(vehicle_name, operation_name)] = end_var
            self.intervals[(vehicle_name, operation_name)] = int_var

            self.operation_var_dict_by_vehicle_operation_dict[(vehicle_name, operation_name)] = int_var
