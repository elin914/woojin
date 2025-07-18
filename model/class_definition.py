class Operation:
    def __init__(self, operation_name, order, test_operation, type_TC, department):
        self.operation_name = operation_name
        self.order = order
        self.test_operation = test_operation  # True or False, 검사 공정 여부
        self.type_TC = type_TC  # True or False
        self.department = department  # 담당공정
        # self.position = position
        self.duration = 1
        self.resource = 1
        # self.left_vehicle_list = list()


class Calendar:
    def __init__(self):
        self.holiday = list()
        self.saturday = list()
        self.index_to_day_calendar_dict = dict()
        self.day_to_index_calendar_dict = dict()


class Vehicle:
    def __init__(self, vehicle_name, type_TC):
        self.vehicle_name = vehicle_name
        self.order = None
        self.type_TC = type_TC
        self.operation_dict = dict()
        self.operation_list = list()

    def add_operation(self, operation, date):
        if operation not in self.operation_dict:
            self.operation_dict[operation] = date
        # else:
        #     if date > self.operation_dict[operation]:
        #         self.operation_dict[operation] = date
