import pandas as pd
import os
import time


def create_config():
    config = dict()

    config['run_time'] = 180
    # single_solution, multiple_solution
    config['search_method'] = 'single_solution'
    config['load_max'] = 33
    # ortools, ilog
    config['model'] = 'ilog'

    config['use_API'] = True
    config['output_save_API'] = True
    config['API_ID'] = 'csdtpcp'
    config['API_PASSWORD'] = 'dtpcp!@'
    config['start_time'] = '2021-08-01'
    config['end_time'] = '2021-10-31'
    config['project_id'] = 'e672bd1e-5ed0-4baa-9cbd-50db20ea24db'
    config['data_file_path1'] = '../data/생관3-612-24-031_2025년 1월 일일생산계획 및 업체별 차종현황_Rev.00_24.12.31(확정).xlsx'
    config['data_file_path2'] = '../data/생관3-612-25-001_2025년 2월 일일생산계획 및 업체별 차종현황_Rev.00_25.01.24(확정).xlsx'
    config['data_file_path3'] = '../data/생관3-612-25-003_2025년 3월 일일생산계획 및 업체별 차종현황_Rev.00_25.02.28(확정).xlsx'
    # config['extra_data_file_path'] = '../data/02.의장·전기·기장 제작 계획 및 실적(24년 12월 예상실적).xlsm'

    config['plot_network'] = True

    # 결과 저장
    config['ymd'] = time.strftime('%Y%m%d')
    config['hour'] = str(time.localtime().tm_hour)
    config['minute'] = str(time.localtime().tm_min)
    config['second'] = str(time.localtime().tm_sec)
    config["folderpath"] = '../results/{0}_{1}h_{2}m_{3}s'.format(config['ymd'], config['hour'], config['minute'], config['second'])

    if not os.path.exists(config["folderpath"]):
        os.makedirs(config["folderpath"], exist_ok=True)

    config_df = pd.json_normalize(config, sep='_').transpose()
    config_df.to_excel(config['folderpath'] + '/configuration.xlsx', index=True)

    return config
