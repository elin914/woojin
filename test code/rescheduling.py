from functions import *

np.bool = np.bool_
from docplex.cp.model import *
import networkx as nx

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

process_list = list(df_data.index.drop_duplicates())

result1 = []
result2 = []
temp_list = []
temp_list1 = []
temp_list2 = []
except_list = []
except_list1 = []
except_list2 = []

except_count = {}  # 전체 예외 횟수 추적
except_count1 = {}  # except_list1에 대한 예외 횟수 추적
except_count2 = {}  # except_list2에 대한 예외 횟수 추적

process_count_dict = {process: 0 for process in process_list}
max_date = 0
for name, subway_car in subway_car_dict.items():
    temp_name_date = []
    for process in process_list:
        if process not in subway_car.activity_dict:
            continue
        activity_name = process
        date = subway_car.activity_dict[activity_name]

        max_date = max(date, max_date)

        process_count_dict[process] += 1
        if temp_name_date == []:
            pass
        else:
            for (temp_name, temp_date) in temp_name_date:
                idx_pair = (process_list.index(temp_name), process_list.index(activity_name))
                if temp_date == date:
                    result1.append(idx_pair)
                    if idx_pair in temp_list1:
                        except_list1.append(idx_pair)
                    else:
                        temp_list1.append(idx_pair)
                elif temp_date + 1 == date:
                    result2.append(idx_pair)
                    if idx_pair in temp_list2:
                        except_list2.append(idx_pair)
                    else:
                        temp_list2.append(idx_pair)
                else:
                    if idx_pair in temp_list:
                        except_list.append(idx_pair)
                    else:
                        temp_list.append(idx_pair)
                    if idx_pair in temp_list1:
                        except_list1.append(idx_pair)
                    else:
                        temp_list1.append(idx_pair)
                    if idx_pair in temp_list2:
                        except_list2.append(idx_pair)
                    else:
                        temp_list2.append(idx_pair)
        temp_name_date.append((activity_name, date))

performance_result = process_count_dict[process_list[-1]]
max_date += 1

# 결론 1: result1 + result2에서 except_list와 2번 이상 어긋난 항목 제외
# final_result1 = sorted(list((set(result1 + result2)) - set(except_list)))
final_result1 = sorted(list((set(result1 + result2)) - set(temp_list)))

# 결론 2: result1에서 except_list2와 2번 이상 어긋난 항목 제외
# final_result2 = sorted(list(set(result1) - set(except_list2)))
final_result2 = sorted(list(set(result1) - set(temp_list2)))

# 결론 3: result2에서 except_list1과 2번 이상 어긋난 항목 제외
# final_result3 = sorted(list(set(result2) - set(except_list1)))
final_result3 = sorted(list(set(result2) - set(temp_list1)))

edges1 = [item for item in final_result1]
edges2 = [item for item in final_result2]

G = nx.DiGraph()  # 유향 그래프
G.add_edges_from(edges1)

connected_components = list(nx.weakly_connected_components(G))  # 약 연결 컴포넌트
sorted_components1 = [sorted(list(component)) for component in connected_components]

G = nx.DiGraph()  # 유향 그래프
G.add_edges_from(edges2)

connected_components = list(nx.weakly_connected_components(G))  # 약 연결 컴포넌트
sorted_components2 = [sorted(list(component)) for component in connected_components]

TC_process_list = [process_list.index(process) for (process, value) in process_count_dict.items() if
                   value < max(process_count_dict.values()) / 2]

sequence_constraint = [
    [element for element in inner_list if element not in TC_process_list]
    for inner_list in sorted_components1
]

# 휴리스틱
sequence_constraint_TC = sorted_components1

same_sequence_constraint = [
    [element for element in inner_list if element not in TC_process_list]
    for inner_list in sorted_components2
]
same_sequence_constraint = [inner_list for inner_list in same_sequence_constraint if len(inner_list) > 1]

same_sequence_constraint_TC = sorted_components2

start_after_10_end_before_27 = sequence_constraint[1] + [16]
sequence_constraint = sequence_constraint[0] + sequence_constraint[2] + sequence_constraint[3]
sequence_constraint_TC = sequence_constraint_TC[0] + sequence_constraint_TC[2] + sequence_constraint_TC[3]

same_sequence_constraint_list = []
same_sequence_constraint_dict = {}
same_sequence_constraint_list_TC = []
same_sequence_constraint_dict_TC = {}
for sequence in same_sequence_constraint:
    same_sequence_constraint_dict[sequence[0]] = sequence[1:]
    for index in sequence[1:]:
        same_sequence_constraint_list.append(index)
for sequence in same_sequence_constraint_TC:
    same_sequence_constraint_dict_TC[sequence[0]] = sequence[1:]
    for index in sequence[1:]:
        same_sequence_constraint_list_TC.append(index)
sequence_constraint = [index for index in sequence_constraint if index not in same_sequence_constraint_list]
sequence_constraint_TC = [index for index in sequence_constraint_TC if index not in same_sequence_constraint_list_TC]

print('TC 전용 작업:', TC_process_list)
print('---------------------------')
print('10 후 27 이전 작업:', start_after_10_end_before_27)
print('---------------------------')
print('선후행 제약:', sequence_constraint)
print('---------------------------')
print('동시 작업 제약:', same_sequence_constraint)
print('---------------------------')
print('선후행 제약 with TC:', sequence_constraint_TC)
print('---------------------------')
print('동시 작업 제약 with TC:', same_sequence_constraint_TC)
print('---------------------------')

# 제약 조건
## 앞선 작업이 먼저 이루어져야한다
## 하나의 작업은 하루에 차 두개까지 수행 가능
## 하나의 차가 하루에 두 작업도 수행 가능
## 동시 작업이 있으면 무조건 같은 날 수행 << 묶어서 인풋 넣기
## 전체 작업 개수 제한 << 무조건 14개만 결과뽑기
## TC에서 16번 작업은 2번째 27번 작업이 끝나기 전에 끝나야함


## B 작업 시키는걸 어디까지 할지 정하기 << 기준의 부재
# 27이 있는 애들은 다 B 작업을 했나?

for name, subway_car in subway_car_dict.items():
    subway_car.min_date_index = min([process_list.index(process) for process in list(subway_car.activity_dict)])
    subway_car.activity_indices = [process_list.index(process) for process in list(subway_car.activity_dict)
                                   if process_list.index(process) not in start_after_10_end_before_27 + same_sequence_constraint_list_TC]
    subway_car.min_date_index_wo_special = min(subway_car.activity_indices)
    if subway_car.min_date_index >= 16:
        subway_car.special_activity_indices = [process_list.index(process) for process in list(subway_car.activity_dict)
                                               if process_list.index(process) in start_after_10_end_before_27]
    else:
        subway_car.special_activity_indices = start_after_10_end_before_27

    # print([process_list.index(process) for process in list(subway_car.activity_dict)])

mdl = CpoModel()

step_by_process_dict = {}
print(same_sequence_constraint_list_TC)
for index in range(len(process_list)):
    if index in [31, 33] or index not in same_sequence_constraint_list_TC:
        step_by_process_dict[index] = step_at(0, 0)

step_by_subway_car_dict = {}
for name, _ in subway_car_dict.items():
    step_by_subway_car_dict[name] = step_at(0, 0)

subway_car_interval_dict = {}
subway_car_special_interval_dict = {}
obj = 0
obj_integer = integer_var(min=14, max=15)
for name, subway_car in subway_car_dict.items():
    interval_dict = {}
    special_interval_dict = {}
    first_interval_special = False
    if 'TC' in name:
        for index in subway_car.special_activity_indices:
            if index == subway_car.min_date_index:
                special_interval_dict[index] = interval_var(size=1, start=subway_car.activity_dict[
                    process_list[subway_car.min_date_index]], optional=False)
                first_interval_special = True
            else:
                special_interval_dict[index] = interval_var(size=1, start=(0, max_date - 1), optional=True)

            step_by_process_dict[index] += mdl.pulse(special_interval_dict[index], 1)
            step_by_subway_car_dict[name] += mdl.pulse(special_interval_dict[index], 1)
        subway_car_special_interval_dict[name] = special_interval_dict

        for index in sequence_constraint_TC[sequence_constraint_TC.index(subway_car.min_date_index_wo_special):]:
            if index == subway_car.min_date_index_wo_special:
                if first_interval_special:
                    interval_dict[index] = interval_var(size=1, start=(0, max_date - 1), optional=True)
                else:
                    interval_dict[index] = interval_var(size=1, start=subway_car.activity_dict[
                        process_list[subway_car.min_date_index_wo_special]], optional=False)
                before_index = index
            else:
                interval_dict[index] = interval_var(size=1, start=(0, max_date - 1), optional=True)
                mdl.add(mdl.end_before_start(interval_dict[index], interval_dict[before_index]))

            if index in list(same_sequence_constraint_dict_TC.keys()):
                step_by_process_dict[index] += mdl.pulse(interval_dict[index], 2)
                step_by_subway_car_dict[name] += mdl.pulse(interval_dict[index], 2)
            else:
                step_by_process_dict[index] += mdl.pulse(interval_dict[index], 1)
                step_by_subway_car_dict[name] += mdl.pulse(interval_dict[index], 1)

            if index == 46:
                obj += mdl.presence_of(interval_dict[index])
        subway_car_interval_dict[name] = interval_dict

    else:
        for index in subway_car.special_activity_indices:
            if index == subway_car.min_date_index:
                special_interval_dict[index] = interval_var(size=1, start=subway_car.activity_dict[process_list[subway_car.min_date_index]], optional=False)
                first_interval_special = True
            else:
                special_interval_dict[index] = interval_var(size=1, start=(0, max_date - 1), optional=True)

            step_by_process_dict[index] += mdl.pulse(special_interval_dict[index], 1)
            step_by_subway_car_dict[name] += mdl.pulse(special_interval_dict[index], 1)
        subway_car_special_interval_dict[name] = special_interval_dict

        for index in sequence_constraint[sequence_constraint.index(subway_car.min_date_index_wo_special):]:
            if index == 2:
                print(index)
            if index == subway_car.min_date_index_wo_special:
                if first_interval_special:
                    interval_dict[index] = interval_var(size=1, start=(0, max_date - 1), optional=True)
                else:
                    interval_dict[index] = interval_var(size=1, start=subway_car.activity_dict[process_list[subway_car.min_date_index_wo_special]], optional=False)
                before_index = index
            else:
                interval_dict[index] = interval_var(size=1, start=(0, max_date - 1), optional=True)
                mdl.add(mdl.end_before_start(interval_dict[index], interval_dict[before_index]))

            if index in list(same_sequence_constraint_dict.keys()):
                step_by_process_dict[index] += mdl.pulse(interval_dict[index], 2)
                step_by_subway_car_dict[name] += mdl.pulse(interval_dict[index], 2)
            else:
                step_by_process_dict[index] += mdl.pulse(interval_dict[index], 1)
                step_by_subway_car_dict[name] += mdl.pulse(interval_dict[index], 1)

            if index == 46:
                obj += mdl.presence_of(interval_dict[index])
        subway_car_interval_dict[name] = interval_dict

    for index, value in special_interval_dict.items():
        mdl.add(end_before_start(value, interval_dict[28]))


    # print(name, interval_dict)
    # print(name, special_interval_dict)

mdl.add(obj == obj_integer)
mdl.add(mdl.maximize(obj))
for index in range(len(process_list)):
    if index in [31, 33] or index not in same_sequence_constraint_list_TC:
        mdl.add(step_by_process_dict[index] <= 2)

for name, _ in subway_car_dict.items():
    mdl.add(step_by_subway_car_dict[name] <= 2)

sol = mdl.solve()
result = 0
for name, interval_dict in subway_car_interval_dict.items():
    result += sol.get_var_solution(interval_dict[46]).presence

print(f"실적 결과: {performance_result}대 완성, 최적화 결과: {result}대 완성")

