import pandas as pd
import numpy as np


def clean_column_names(df):
    columns = df.columns.tolist()
    for i in range(1, len(columns)):  # 첫 번째 열은 처리할 필요 없음
        if isinstance(columns[i], str) and "Unnamed" in columns[i]:
            columns[i] = columns[i - 1]  # 바로 왼쪽 열 이름으로 대체
    df.columns = columns
    return df


class SubwayCar:
    def __init__(self, name):
        self.name = name
        self.activity_dict = dict()
        self.min_index_dict = dict()
        self.min_date_index = None

    def add_activity(self, activity_name, date):
        if activity_name not in self.activity_dict:
            self.activity_dict[activity_name] = date
        else:
            print(f"subwaycar {self.name} activity {activity_name}: {date} is already taken")


def create_subway_car_dict(df_data, subway_car_dict, start_date):
    temp = list(dict.fromkeys(df_data.columns))
    for col_idx in range(df_data.shape[1]):
        date = df_data.columns[col_idx]  # 현재 열의 이름

        for row_idx in range(df_data.shape[0]):  # 행 반복
            activity_name = df_data.index[row_idx]  # 현재 행 이름
            car_name = df_data.iloc[row_idx, col_idx]  # 값 가져오기

            if pd.notna(car_name):  # NaN 값 제외
                if car_name not in subway_car_dict:
                    subway_car_dict[car_name] = SubwayCar(name=car_name)
                # subway_car_dict[car_name].add_activity(activity_name, start_date + pd.Timedelta(days=date - 1))
                subway_car_dict[car_name].add_activity(activity_name, temp.index(date))
    return subway_car_dict
