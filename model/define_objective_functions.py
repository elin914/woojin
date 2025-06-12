def define_object_functions(self):
    for (vehicle_name, operation), var in self.operation_var_dict_by_vehicle_operation.items():
        self.load_step_function += self.model.pulse(var, 1)

    self.model.add(self.load_step_function <= self.max_load)
    self.model.add(self.model.minimize(self.max_load))

    # 부하 최적화
