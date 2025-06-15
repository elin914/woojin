def define_variables(self):
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation_name in vehicle.operation_list:
            self.operation_var_dict_by_vehicle_operation_dict[(vehicle_name, operation_name)]\
                = self.model.interval_var(start=(self.start_time_index, self.end_time_index),
                                          end=(self.start_time_index, self.end_time_index),
                                          size=1, name=f"{vehicle_name}_{operation_name}")
