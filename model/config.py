import pandas as pd
import os
import time


def create_config():
    config = dict()

    config['run_time'] = 10

    config['use_API'] = False
    config['API_ID'] = None
    config['data_file_path'] = '../data/생관3-612-24-031_2025년 1월 일일생산계획 및 업체별 차종현황_Rev.00_24.12.31(작성중).xlsx'
    # config['extra_data_file_path'] = '../data/02.의장·전기·기장 제작 계획 및 실적(24년 12월 예상실적).xlsm'

    # 결과 저장
    config['ymd'] = time.strftime('%Y%m%d')
    config['hour'] = str(time.localtime().tm_hour)
    config['minute'] = str(time.localtime().tm_min)
    config['second'] = str(time.localtime().tm_sec)
    config["folderpath"] = '../results/{0}_{1}h_{2}m_{3}s'.format(config['ymd'], config['hour'], config['minute'], config['second'])

    if not os.path.exists(config["folderpath"]):
        os.mkdir(config["folderpath"])

    config_df = pd.json_normalize(config, sep='_').transpose()
    config_df.to_excel(config['folderpath'] + '/configuration.xlsx', index=True)

    return config
