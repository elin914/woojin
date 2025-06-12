def define_constraints(self):
    # 검사 기간 사이의 그룹 내 선후행 제약
    # 동시작업
    for (vehicle_name, operation), var in self.operation_var_dict_by_vehicle_operation.items():
        # 토요일 검사 불가능
        if self.operation_dict[operation].test_operation:
            for saturday_index in self.calendar.saturday:
                self.model.add(self.model.start_of(var) != saturday_index)
        # 휴일 작업 불가능
        for holiday_index in self.calendar.holiday:
            self.model.add(self.model.start_of(var) != holiday_index)

    pass
