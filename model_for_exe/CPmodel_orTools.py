import numpy as np
from ortools.sat.python import cp_model
import pandas as pd
from get_data import *
from define_variables_orTools import *
from define_constraints_orTools import *
from define_objective_functions_orTools import *
from save_results_orTools import *


class CPmodel:
    def __init__(self, config):
        self.config = config
        self.model = cp_model.CpModel()
        self.solver = None
        self.status = None
        self.search_start_time = None
        self.solution = None
        self.start_time = self.config['start_date']
        self.end_time = self.config['end_date']
        self.start_time_index = 0
        # self.end_time_index = 31
        self.end_time_index = None
        self.load_max = None

        self.df_process = pd.DataFrame()
        self.df_vehicle = pd.DataFrame()
        self.process_list = list()
        self.operation_list = list()
        self.test_operation_list = list()
        self.TC_operation_list = list()
        self.operation_dict = dict()
        self.operation_id_to_key_dict = dict()
        self.same_sequence_constraint = list()
        self.calendar = None
        self.vehicle_dict = dict()
        self.operation0_dict = dict()  # vehicle_name: date
        self.load_step_dict = list()
        
        self.capacity = None
        
        self.starts = {}
        self.ends = {}
        self.intervals = {}

        self.max_load = None
        self.min_load = None

        self.load_step_function = None
        self.load_step_function2 = None
        self.operation_var_dict_by_vehicle_operation_dict = dict()
        self.step_function_by_operation_dict = dict()
        self.step_function_by_vehicle_dict = dict()

    def get_data(self):
        print("\n===== API를 통한 데이터 요청 시작 =====")
        get_data_from_api(self)
        print("===== API를 통한 데이터 로딩 완료! =====")

    def run_model(self):
        print("===== 최적화 모델 시작 =====")
        print("\n==== 변수 모델링 진행 중... ====")
        define_variables(self)
        print("==== 변수 모델링 완료! ====")
        print("\n==== 제약 조건 모델링 진행 중... ====")
        define_constraints(self)
        print("==== 제약 조건 모델링 완료! ====")
        print("\n==== 목적 함수 모델링 진행 중... ====")
        define_object_functions(self)
        print("==== 목적 함수 모델링 완료! ====")

        print("\n==== 최적화 모델 해 탐색 시작 ====")
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True
        solver.parameters.max_time_in_seconds = self.config['run_time']

        status = solver.Solve(self.model)

        self.solver = solver
        self.status = status
        print("==== 최적화 모델 해 탐색 완료 ====")
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print("해를 발견했습니다.")
            print("\n===== 결과 정리 시작 =====")
            save_results(self)
            print("===== 결과 정리 완료 =====")
            return True
        else:
            print("해를 발견하지 못했습니다.")
            return False
