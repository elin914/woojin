def define_object_functions(self):
    
    # peak_load: 모든 interval을 모아 동시에 실행될 수 있는 작업 수의 상한
    all_intervals = list(self.operation_var_dict_by_vehicle_operation_dict.values())
    self.peak_load = self.model.NewIntVar(0, self.capacity, "peak_load")
    
    if all_intervals:
        self.model.AddCumulative(all_intervals, [1] * len(all_intervals), self.peak_load)

    self.model.Minimize(self.peak_load)
    