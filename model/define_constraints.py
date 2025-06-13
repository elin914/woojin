def define_constraints(self):
    # 검사 기간 사이의 그룹 내 선후행 제약
    self.step_function_by_operation_dict = {operation: self.model.step_at(0, 0) for operation in self.operation_list}
    self.step_function_by_vechicle_dict = {vehicle_name: self.model.step_at(0, 0) for vehicle_name in
                                           self.vehicle_dict.keys()}
    for (vehicle_name, operation), var in self.operation_var_dict_by_vehicle_operation_dict.items():
        # 흡음재 취부 일정 고정
        if self.operation_dict[operation].order == 0:
            self.model.add(self.model.start_of(var) == self.operation0_dict[vehicle_name])
        # 토요일 검사 불가능
        if self.operation_dict[operation].test_operation:
            for saturday_index in self.calendar.saturday:
                self.model.add(self.model.start_of(var) != saturday_index)
        # 휴일 작업 불가능
        for holiday_index in self.calendar.holiday:
            self.model.add(self.model.start_of(var) != holiday_index)
        same_sequence_condition = True
        # 공정 별 capacity, 동시 작업 시 추가하지 않음
        for same_sequence in self.same_sequence_constraint:
            if self.operation_list.index(operation) in same_sequence[1:]:
                same_sequence_condition = False
            for (vehicle_name2, operation2), var2 in self.operation_var_dict_by_vehicle_operation_dict.items():
                if vehicle_name == vehicle_name2 and operation != operation2:
                    # 동시 작업 공정 추가
                    if operation in same_sequence and operation2 in same_sequence:
                        self.model.add(self.model.start_of(var) == self.model_start_of(var2))
                    # 공정이 끝나야 검사 수행 가능
                    elif (self.operation_dict[operation].order < self.operation_dict[operation2].order
                          and self.operation_dict[operation2].test_operation):
                        self.model.add(self.model.end_of(var) <= self.model.start_of(var2))
                    # 그룹 내 선후행 제약
                    elif (self.operation_dict[operation].order < self.operation_dict[operation2].order
                          and self.operation_dict[operation].department == self.operation_dict[operation2].department):
                        self.model.add(self.model.end_of(var) <= self.model.start_of(var2))
        if same_sequence_condition:
            self.step_function_by_operation_dict[operation] += self.model.pulse(var, 1)
            self.step_function_by_vechicle_dict[vehicle_name] += self.model.pulse(var, 1)

    # 공정 별 capacity 제약
    for step_function_by_operation in self.step_function_by_operation_dict.values():
        self.model.add(step_function_by_operation <= 2)
    for step_function_by_vechicle in self.step_function_by_vechicle_dict.values():
        self.model.add(step_function_by_vechicle <= 2)
