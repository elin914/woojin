# def define_variables(self):
#     self.load_step_function = self.model.step_at(0, 0)
#     self.load_step_function2 = self.model.step_at(0, 0) + self.model.pulse(
#         (self.start_time_index, self.end_time_index + 1), self.config['load_max'])
#     for vehicle_name, vehicle in self.vehicle_dict.items():
#         for operation_name in vehicle.operation_list:
#             self.operation_var_dict_by_vehicle_operation_dict[(vehicle_name, operation_name)]\
#                 = self.model.interval_var(start=(self.start_time_index, self.end_time_index),
#                                           end=(self.start_time_index, self.end_time_index + 1),
#                                           size=1, name=f"{vehicle_name}_{operation_name}")

def define_variables(self) :
    for vehicle_name, vehicle in self.vehicle_dict.items():
        for operation_name in vehicle.operation_list:
            start_var = self.model.NewIntVar(self.start_time_index, self.end_time_index)
            duration = 1
            end_var = self.model.NewIntVar(self.start_time_index + duration, self.end_time_index + duration)
            
            self.operation_var_dict_by_vehicle_operation_dict[(vehicle_name, operation_name)]\
             = self.model.NewIntervalVar(start_var, duration, end_var, f'{vehicle_name}_{operation_name}_interval')