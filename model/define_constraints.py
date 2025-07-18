def define_constraints(self):
    # 검사 기간 사이의 그룹 내 선후행 제약
    self.step_function_by_operation_dict = {operation: self.model.step_at(0, 0) for operation in self.operation_list}
    self.step_function_by_vehicle_dict = {vehicle_name: self.model.step_at(0, 0) for vehicle_name in
                                          self.vehicle_dict.keys()}
    for (vehicle_name, operation_name), var in self.operation_var_dict_by_vehicle_operation_dict.items():
        # 흡음재 취부 일정 고정
        if self.operation_dict[operation_name].order == 0:
            self.model.add(self.model.start_of(var) == self.operation0_dict[vehicle_name])
        # 토요일 검사 불가능
        if self.operation_dict[operation_name].test_operation:
            for saturday_index in self.calendar.saturday:
                self.model.add(self.model.start_of(var) != saturday_index)
        # 휴일 작업 불가능
        for holiday_index in self.calendar.holiday:
            self.model.add(self.model.start_of(var) != holiday_index)
        # 공정 별 capacity, 동시 작업 시 추가하지 않음
        same_sequence_condition = True
        for same_sequence in self.same_sequence_constraint:
            if self.operation_list.index(operation_name) in same_sequence[1:]:
                same_sequence_condition = False
                if (vehicle_name,
                    self.operation_list[same_sequence[0]]) in self.operation_var_dict_by_vehicle_operation_dict:
                    self.model.add(self.model.start_of(var) == self.model.start_of(
                        self.operation_var_dict_by_vehicle_operation_dict[
                            (vehicle_name, self.operation_list[same_sequence[0]])]))
                break
        if same_sequence_condition:
            self.step_function_by_operation_dict[operation_name] += self.model.pulse(var, 1)
            self.step_function_by_vehicle_dict[vehicle_name] += self.model.pulse(var, 1)

        for (vehicle_name2, operation_name2), var2 in self.operation_var_dict_by_vehicle_operation_dict.items():
            same_sequence_condition2 = True
            for same_sequence in self.same_sequence_constraint:
                if self.operation_list.index(operation_name2) in same_sequence[1:]:
                    same_sequence_condition2 = False
                    break
            if same_sequence_condition2 is False:
                continue

            if vehicle_name == vehicle_name2 and operation_name != operation_name2:
                # 공정이 끝나야 검사 수행 가능
                if (self.operation_dict[operation_name].order < self.operation_dict[operation_name2].order
                        and self.operation_dict[operation_name2].test_operation):
                    self.model.add(self.model.end_of(var) <= self.model.start_of(var2))
                elif (self.operation_dict[operation_name].order < self.operation_dict[operation_name2].order
                      and self.operation_dict[operation_name].test_operation):
                    self.model.add(self.model.end_of(var) <= self.model.start_of(var2))
                # 그룹 내 선후행 제약
                elif (self.operation_dict[operation_name].order < self.operation_dict[operation_name2].order
                      and self.operation_dict[operation_name].department == self.operation_dict[
                          operation_name2].department):
                    self.model.add(self.model.end_of(var) <= self.model.start_of(var2))
            if vehicle_name != vehicle_name2 and operation_name == operation_name2 and self.vehicle_dict[
                vehicle_name].order < self.vehicle_dict[vehicle_name2].order - 2:
                self.model.add(self.model.start_of(var) <= self.model.start_of(var2))

    # 공정 별 capacity 제약
    for step_function_by_operation in self.step_function_by_operation_dict.values():
        self.model.add(step_function_by_operation <= 2)
    for step_function_by_vehicle in self.step_function_by_vehicle_dict.values():
        self.model.add(step_function_by_vehicle <= 2)
