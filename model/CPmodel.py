import numpy as np

np.bool = np.bool_
from docplex.cp.model import *
import pandas as pd
from get_data import *
from define_variables import *
from define_constraints import *
from define_objective_functions import *
from save_results import *
from plot_network import *


class CPmodel:
    def __init__(self, config):
        self.config = config
        self.model = CpoModel()
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
        # self.max_load = self.model.integer_var()
        self.max_load = self.model.integer_var(0, self.config['load_max'])
        # self.min_load = self.model.integer_var()
        self.min_load = self.model.integer_var(0, self.config['load_max'])
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
        define_variables(self)
        print("Define Variables Completed")
        define_constraints(self)
        print("Define Constraints Completed")
        define_object_functions(self)
        print("Define Object Functions Completed")
        self.search_start_time = time.time()
        if self.config['search_method'] == 'multiple_solution':
            self.solution = self.model.start_search(TimeLimit=self.config['run_time'])
        else:
            self.solution = self.model.solve(TimeLimit=self.config['run_time'])
        save_results(self)

    def plot_network(self):
        if self.config['plot_network']:
            plot_network(self)
            print("Plot Network Completed")
        else:
            print("No Network")
