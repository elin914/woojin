import numpy as np

np.bool = np.bool_
from docplex.cp.model import *
import pandas as pd
from get_data import *
from define_variables import *
from define_constraints import *
from define_objective_functions import *
from save_results import *


class CPmodel:
    def __init__(self, config):
        self.config = config
        self.model = CpoModel()
        self.search_start_time = None
        self.solution = None
        self.start_time_index = 0
        self.end_time_index = 31

        self.df_process = pd.DataFrame()
        self.df_vehicle = pd.DataFrame()
        self.process_list = list()
        self.operation_list = list()
        self.test_operation_list = list()
        self.TC_operation_list = list()
        self.operation_dict = dict()
        self.same_sequence_constraint = list()
        self.calendar = None
        self.vehicle_dict = dict()

        self.operation0_dict = dict()  # vehicle_name: date

        self.max_load = self.model.integer_var()
        # self.max_load = self.model.integer_var(0, 40)
        self.load_step_function = self.model.step_at(0, 0)
        self.operation_var_dict_by_vehicle_operation_dict = dict()
        self.step_function_by_operation_dict = dict()
        self.step_function_by_vechicle_dict = dict()

    def get_data(self):
        if self.config['use_API']:
            pass
        else:
            get_data_from_xlsx(self)

    def run_model(self):
        define_variables(self)
        print("Define Variables Completed")
        define_constraints(self)
        print("Define Constraints Completed")
        define_object_functions(self)
        print("Define Object Functions Completed")
        self.search_start_time = time.time()
        # self.solution = self.model.start_search(TimeLimit=self.config['run_time'])
        self.solution = self.model.solve(TimeLimit=self.config['run_time'])
        save_results(self)
