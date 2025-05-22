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

        self.df_process = pd.DataFrame()
        self.df_vehicle = pd.DataFrame()
        self.process_list = list()
        self.operation_list = list()
        self.test_opeartion_list = list()
        self.TC_operation_list = list()
        self.operation_dict = dict()
        self.same_sequence_constarint = list()
        self.calendar = None
        self.vehicle_dict = dict()

        self.operation0_dict = dict()  # vehicle_name: date

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
        self.solution = self.model.start_search(TimeLimit=self.config['run_time'])
        save_results(self)
