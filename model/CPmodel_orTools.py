import numpy as np

np.bool = np.bool_
from ortools.sat.python import cp_model
import pandas as pd
from get_data import *
from define_variables_orTools import *
from define_constraints_orTools import *
from define_objective_functions_orTools import *
from save_results_orTools import *
from plot_network import *


class CPmodel:
    def __init__(self, config):
        self.config = config
        self.model = cp_model.CpModel()
        self.solver = None
        self.status = None
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
        
        self.capacity = int(self.config['load_max'])
        
        self.starts = {}
        self.ends = {}
        self.intervals = {}
        
        self.max_load = self.model.NewIntVar(0, self.config['load_max'], f'max_load')
        self.min_load = self.model.NewIntVar(0, self.config['load_max'], f'min_load')

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
        define_variables(self)
        define_constraints(self)
        define_object_functions(self)

        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True
        solver.parameters.max_time_in_seconds = self.config['run_time']

        status = solver.Solve(self.model)

        self.solver = solver
        self.status = status

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print("Solution found")
        else:
            print("Cannot find a feasible solution")

        save_results(self)

    def plot_network(self):
        if self.config['plot_network']:
            plot_network(self)
            print("Plot Network Completed")
        else:
            print("No Network")
