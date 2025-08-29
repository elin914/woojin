import pandas as pd
import os
import time


def load_config(start_time, start_date, end_date):
    """
    config.txt 파일을 읽어와 설정을 로드하고,
    동적인 결과 폴더 경로를 추가하여 반환하는 함수.
    """
    config = dict()
    config['program_start_time'] = start_time
    config['start_date'] = start_date
    config['end_date'] = end_date
    config['run_time'] = 300
    try:
        with open('config.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 빈 줄이거나 주석(#)은 건너뛰기
                if not line or line.startswith('#'):
                    continue

                # '='을 기준으로 key와 value 분리
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        print("오류: config.txt 파일이 존재하지 않습니다.")
        return None

    # config['ymd'] = time.strftime('%Y%m%d')
    # config['hour'] = str(time.localtime().tm_hour)
    # config['minute'] = str(time.localtime().tm_min)
    # config['second'] = str(time.localtime().tm_sec)
    # config["folderpath"] = '{0}_{1}h_{2}m_{3}s'.format(config['ymd'], config['hour'], config['minute'],
    #                                                               config['second'])

    if not os.path.exists(config["folderpath"]):
        os.makedirs(config["folderpath"], exist_ok=True)

    try:
        config_df = pd.json_normalize(config, sep='_').transpose()
        config_df.to_excel(config['folderpath'] + '/configuration.xlsx', index=True)
    except Exception as e:
        print(f"엑셀 저장 중 오류 발생: {e}")

    return config
