from functions import *

np.bool = np.bool_
from docplex.cp.model import *

df_name = pd.read_excel('../data/생관3-612-24-007_2024년 4월 일일생산계획 및 업체별 차종현황_Rev.00_24.03.28(확정).xlsx',
                        skiprows=[0, 1, 2], usecols='C', nrows=64)
df_data = pd.read_excel('../data/생관3-612-24-007_2024년 4월 일일생산계획 및 업체별 차종현황_Rev.00_24.03.28(확정).xlsx',
                        skiprows=[0, 1, 2, 3], usecols='F:BE', nrows=64)

df_name = df_name.drop(index=df_name.index[0])
df_name = df_name.reset_index(drop=True)
df_name = df_name.map(lambda x: x.strip() if isinstance(x, str) else x)
df_name = df_name.ffill()
df_data = df_data.drop(index=df_data.index[-1])
df_data = df_data.drop(index=df_data.index[-1])
df_data.index = df_name['세부공정명'].tolist()

# DataFrame 열 이름 정리
df_data = clean_column_names(df_data)

subway_car_dict = {}  # {name: SubwayCar 객체}
subway_car_dict = create_subway_car_dict(df_data, subway_car_dict, pd.to_datetime('2024-04-01'))

process_list = [
    "흡음재 취부", "흡음재 씰링/검사/수정", "측창취부/T-BOLT 삽입", "실내/상하 CABLE HARNESS 취부", "실내/상하 배선",
    "실내 배선 작업", "객실도어 취부", "리무벌/파티션 프레임 취부", "객실도어 취부 검사", "하부덕트검사\n (D+1~4일차 조정작업)",
    "실내 배선 검사", "AIR DUCT MODULE 취부", "CENTER GRILL 취부", "AIR DUCT MODULE 취부 검사", "CAB MODULE 취부(TC)",
    "배관 MODULE 취부", "배전반 취부 및 배선작업", "CENTER PIVOT 취부", "COUPLER 취부", "제동기기 취부 및 누설검사",
    "운전실 내장판 취부", "D+5~13일차 조정작업", "ROOF 내장판 취부", "운전실 캐비넷 취부(TC)", "상하 전장기기 취부 결선", "SIDE 내장판 취부",
    "운전실 배전반 결선(TC)", "AIR CON 취부", "내장판 조정작업(완료)", "내장판 취부 검사", "운전실 DOOR 취부(TC)", "전장기기 취부 결선 완료",
    "운전실 전장기기 취부 결선(TC)", "도통검사(량단위 시험기)", "도통 자체 검사(완료)", "도통 검사 수정", "도통입회검사/내전압자체검사",
    "내전압 입회검사", "수정작업 및 점검커버 복구", "D+17~20일차 조정작업", "전장취부, 결선 복구 완료", "실내 조정 및 실내·외 설비 완료",
    "전장품 취부 입회검사", "복구 및 수정작업", "실내 설비 입회검사", "대차차입 전검사 / 대차차입", "대차 전장품 취부 결선 & 마무리", "대차차입 후 검사"
]

constraint_list = []
constraint_dict = {}

for car_name, subway_car in subway_car_dict.items():
    for process1, date1 in subway_car.activity_dict.items():
        for process2, date2 in subway_car.activity_dict.items():
            if (process_list.index(process1) < process_list.index(process2)) and (date1 > date2):
                if (process1, process2) not in constraint_list:
                    constraint_list.append((process1, process2))
                    constraint_dict[(process1, process2)] = car_name

mdl = CpoModel()
interval_dict_A = dict()
interval_dict_B = dict()
interval_dict_C = dict()
for process in process_list:
    interval_dict_A[process] = interval_var(size=1, end=(0, 48), optional=True)
    interval_dict_B[process] = interval_var(size=1, end=(0, 48), optional=True)
    interval_dict_C[process] = interval_var(size=1, end=(0, 48), optional=True)
    mdl.add((mdl.presence_of(interval_dict_A[process])
             + mdl.presence_of(interval_dict_B[process]) + mdl.presence_of(interval_dict_C[process])) == 1)

for process in process_list:
    for process2 in process_list[process_list.index(process) + 1:]:
        mdl.add(mdl.end_before_start(interval_dict_A[process], interval_dict_A[process2]))
        mdl.add(mdl.end_before_start(interval_dict_B[process], interval_dict_B[process2]))
        mdl.add(mdl.end_before_start(interval_dict_C[process], interval_dict_C[process2]))
        if (process, process2) in constraint_list:
            mdl.add(((mdl.presence_of(interval_dict_A[process]) * mdl.presence_of(interval_dict_A[process2])) == 0))
            mdl.add(((mdl.presence_of(interval_dict_B[process]) * mdl.presence_of(interval_dict_B[process2])) == 0))
            mdl.add(((mdl.presence_of(interval_dict_C[process]) * mdl.presence_of(interval_dict_C[process2])) == 0))

presence_sum_A = sum(mdl.presence_of(interval_dict_A[process]) for process in process_list)
presence_sum_B = sum(mdl.presence_of(interval_dict_B[process]) for process in process_list)
presence_sum_C = sum(mdl.presence_of(interval_dict_C[process]) for process in process_list)
integer_A = integer_var(min=-1, max=1)
integer_B = integer_var(min=-1, max=1)
integer_C = integer_var(min=-1, max=1)
temp_A = presence_sum_A - presence_sum_B
temp_B = presence_sum_B - presence_sum_C
temp_C = presence_sum_C - presence_sum_A
mdl.add(integer_A * temp_A > 0)
mdl.add(integer_B * temp_B > 0)
mdl.add(integer_C * temp_C > 0)
obj = integer_A * temp_A + integer_B * temp_B + integer_C * temp_C
# mdl.minimize(obj)

sol = mdl.solve()

result_A = []
result_B = []
result_C = []
for process in process_list:
    if sol.get_var_solution(interval_dict_A[process]).presence:
        result_A.append(process)
    if sol.get_var_solution(interval_dict_B[process]).presence:
        result_B.append(process)
    if sol.get_var_solution(interval_dict_C[process]).presence:
        result_C.append(process)

print(result_A)
print(result_B)
print(result_C)

for result in [result_A, result_B, result_C]:
    for car_name, subway_car in subway_car_dict.items():
        temp_list = []
        for process, date in subway_car.activity_dict.items():
            if process in result:
                temp_list.append((result.index(process), date))

        for i in range(len(temp_list) - 1):
            for j in range(i + 1, len(temp_list)):
                index_i, date_i = temp_list[i]
                index_j, date_j = temp_list[j]

                # 조건: index가 더 작은데 날짜가 더 크거나, index가 큰데 날짜가 작은 경우
                if (index_i < index_j and date_i > date_j) or (index_i > index_j and date_i < date_j):
                    print(f"Error in {car_name}")
                    print(f"{result[index_i]} // {result[index_j]}")
                    print(f"Dates: {date_i} and {date_j}")
