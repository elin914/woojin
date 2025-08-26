from config import *
import time 
import numpy as np
from CPmodel_orTools import CPmodel


def main():
    print("\n====== 최적화 프로그램 시작 ======")
    start_time = time.time()
    print("==== config.txt 로드 중... ====")
    config = load_config()
    print("==== config.txt 로드 완료! ====")
    model = CPmodel(config)
    model.get_data()
    model.run_model()
    print("==== 최적화 프로그램 종료 ====")
    print("\n프로그램 총 실행 시간:", np.round(time.time() - start_time, 5))
    print("아무 키나 누르면 종료됩니다.")
    input()


if __name__ == '__main__':
    main()
