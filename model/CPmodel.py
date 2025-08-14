import numpy as np

np.bool = np.bool_
from ortools.sat.python import cp_model
# from docplex.cp.model import *
import time
import pandas as pd
from get_data import *
from define_variables import *
from define_constraints import *
from define_objective_functions import *
from save_results import *

class CPmodel:
    def __init__(self, config):
        self.config = config
        self.model = cp_model.CpModel()
        # self.model = CpoModel()
        self.search_start_time = None
        self.solution = None
        self.start_time = pd.to_datetime(self.config['start_time'])
        self.end_time = pd.to_datetime(self.config['end_time'])
        self.start_time_index = 0
        # self.end_time_index = 31
        self.end_time_index = None

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
        
        self.max_load = self.model.NewIntVar(0, self.config['load_max'], f'max_load')
        # self.max_load = self.model.integer_var(0, self.config['load_max'])
        self.min_load = self.model.NewIntVar(0, self.config['load_max'], f'max_load')
        # self.min_load = self.model.integer_var(0, self.config['load_max'])
        
        # self.load_step_function = self.model.step_at(0, 0)
        # self.load_step_function2 = self.model.step_at(0, 0) + self.model.pulse((self.start_time_index, self.end_time_index + 1), self.config['load_max'])
        self.load_step_function = None
        self.load_step_function2 = None
        self.operation_var_dict_by_vehicle_operation_dict = dict()
        self.step_function_by_operation_dict = dict()
        self.step_function_by_vehicle_dict = dict()

    def get_data(self):
        if self.config['use_API']:
            get_data_from_api(self)
        else:
            get_data_from_xlsx(self)
        print("Load Data Completed")

    def run_model(self):
        
        # added
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True # Search progress log: enabled
        solver.parameters.max_time_in_seconds = self.config['run_time'] # Exploration time cap
        
        status = solver.Solve(self.model)
        
        define_variables(self)
        print("Define Variables Completed")
        define_constraints(self)
        print("Define Constraints Completed")
        define_object_functions(self)
        print("Define Object Functions Completed")
        self.search_start_time = time.time()
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution found")
        else :
            print("Cannot find a feasible solution")
        save_results(self)