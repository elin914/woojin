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
temp_list =[]
temp_list1 =[]
temp_list2 =[]
except_list = []
except_list1 = []
except_list2 = []

except_count = {}    # 전체 예외 횟수 추적
except_count1 = {}   # except_list1에 대한 예외 횟수 추적
except_count2 = {}   # except_list2에 대한 예외 횟수 추적

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

# 결론 1: result1 + result2에서 except_list와 2번 이상 어긋난 항목 제외
final_result1 = sorted(list((set(result1 + result2)) - set(except_list)))
# final_result1 = sorted(list((set(result1 + result2)) - set(temp_list)))

# 결론 2: result1에서 except_list2와 2번 이상 어긋난 항목 제외
final_result2 = sorted(list(set(result1) - set(except_list2)))
# final_result2 = sorted(list(set(result1) - set(temp_list2)))

# 결론 3: result2에서 except_list1과 2번 이상 어긋난 항목 제외
final_result3 = sorted(list(set(result2) - set(except_list1)))
# final_result3 = sorted(list(set(result2) - set(temp_list1)))

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

TC_process_list = [process_list.index(process)for (process, value) in process_count_dict.items() if value < max(process_count_dict.values()) / 2]

sequence_constraint = [
    [element for element in inner_list if element not in TC_process_list]
    for inner_list in sorted_components1
]

# 휴리스틱
sequence_constraint[2].insert(sequence_constraint[2].index(17), 16)

sequence_constraint_TC = sorted_components1

same_sequence_constraint = [
    [element for element in inner_list if element not in TC_process_list]
    for inner_list in sorted_components2
]
same_sequence_constraint = [inner_list for inner_list in same_sequence_constraint if len(inner_list) > 1]

same_sequence_constraint_TC = sorted_components2


indices_dict = {
    'A': sequence_constraint[0],
    'B': sequence_constraint[1],
    'C': sequence_constraint[2],
    'D': sequence_constraint[3],
}
for name, subway_car in subway_car_dict.items():
    subway_car.min_index_dict = dict.fromkeys(indices_dict.keys(), None)
    subway_car.min_date_index = process_list.index(min(subway_car.activity_dict.items(), key=lambda item: item[1])[0])
    for activity_name, date in subway_car.activity_dict.items():
        index = process_list.index(activity_name)
        for key in indices_dict:
            if index in indices_dict[key]:
                if subway_car.min_index_dict[key] is None or subway_car.min_index_dict[key] > index:
                    subway_car.min_index_dict[key] = index

    if not subway_car.min_date_index == min(filter(lambda x: x is not None, subway_car.min_index_dict.values())) or subway_car.min_date_index == 11:
        print(name, subway_car.min_date_index, subway_car.min_index_dict, subway_car.min_date_index == min(filter(lambda x: x is not None, subway_car.min_index_dict.values())))
# 가장 작은 값은 optional=False 로 해야겠네
print(len(list(subway_car_dict.keys())))

start_after_10_end_before_27 = sequence_constraint[1]
sequence_constraint = sequence_constraint[0] + sequence_constraint[2] + sequence_constraint[3]

start_after_10_end_before_27_TC = sequence_constraint_TC[1] + [16]
sequence_constraint_TC = sequence_constraint_TC[0] + sequence_constraint_TC[2] + sequence_constraint_TC[3]

print('TC 전용 작업:', TC_process_list)
print('---------------------------')
print('선후행 제약:', sequence_constraint)
print('---------------------------')
print('10 후 27 이전:', start_after_10_end_before_27)
print('---------------------------')
print('동시 작업 제약:', same_sequence_constraint)
print('---------------------------')
print('작업이 모두 존재하는가?', sorted(sequence_constraint + start_after_10_end_before_27) == sorted(list(set(range(len(process_list))) - set(TC_process_list))))
print('---------------------------')
print('---------------------------')
print('선후행 제약 with TC:', sequence_constraint_TC)
print('---------------------------')
print('10 후 27 이전:', start_after_10_end_before_27_TC)
print('---------------------------')
print('동시 작업 제약 with TC:', same_sequence_constraint_TC)
print('---------------------------')
print('작업이 모두 존재하는가?', sorted(sequence_constraint_TC + start_after_10_end_before_27_TC) == sorted(range(len(process_list))))
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

mdl = CpoModel()



