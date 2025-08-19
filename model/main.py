"""
    orTools용 실행부
"""

from config import *
import time 
import numpy as np
from CPmodel_orTools import CPmodel

def main():
    start_time = time.time()
    
    config = create_config()
    if config['model'] == 'ortools':
        from CPmodel_orTools import CPmodel
    # elif config['model'] == 'ilog':
    #     from CPmodel import
    model = CPmodel(config)
    model.get_data()
    model.run_model()

    print("run time:", np.round(time.time() - start_time, 5))


if __name__ == '__main__':
    main()
