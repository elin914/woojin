from config import *
import time 
import numpy as np
from CPmodel_orTools import CPmodel


def main():
    start_time = time.time()
    
    config = load_config()
    model = CPmodel(config)
    model.get_data()
    model.run_model()
    print("\n 프로그램 총 실행 시간:", np.round(time.time() - start_time, 5))
    print("\n 아무 키나 누르면 종료됩니다.")
    input()


if __name__ == '__main__':
    main()
