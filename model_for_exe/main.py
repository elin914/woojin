from config import *
import time 
import numpy as np
from CPmodel_orTools import CPmodel
import sys
import pandas as pd


def main():
    start_time = time.time()
    if len(sys.argv) != 3:
        print("==== YYYY-MM-DD 형태의 입력 두 가지가 필요합니다 ====")
        sys.exit(1)
    try:
        start_date = pd.to_datetime(sys.argv[1])
        end_date = pd.to_datetime(sys.argv[2])
        print(f"기간이 설정되었습니다: {start_date.date()} ~ {end_date.date()}")
        print("\n====== 최적화 프로그램 시작 ======")
        print("==== config.txt 로드 중... ====")
        config = load_config(start_time, start_date, end_date)
        print("==== config.txt 로드 완료! ====")
        model = CPmodel(config)
        model.get_data()
        solve = model.run_model()
        print("==== 최적화 프로그램 종료 ====")
        if solve:
            return 0
        else:
            return -1
        # print("아무 키나 누르면 종료됩니다.")
        # input()
    except ValueError:
        print("==== YYYY-MM-DD 형태의 입력 두 가지가 필요합니다 ====")
        sys.exit(1)


if __name__ == '__main__':
    main()
