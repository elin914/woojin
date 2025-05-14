import numpy as np

np.bool = np.bool_
from docplex.cp.model import *


class CPmodel:
    def __init__(self, config):
        self.config = config
