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

# process_dict = {
#     'A': ['상하 전장기기 취부 결선', '내장판 조정작업(완료)'],
#     'B': ['리무벌/파티션 프레임 취부', '실내 배선 검사', 'AIR DUCT MODULE 취부', 'CENTER GRILL 취부', 'AIR DUCT MODULE 취부 검사',
#           '배관 MODULE 취부', 'CENTER PIVOT 취부', 'COUPLER 취부', '제동기기 취부 및 누설검사', 'D+5~13일차 조정작업',
#           'ROOF 내장판 취부', 'SIDE 내장판 취부', 'AIR CON 취부', '내장판 취부 검사', '전장기기 취부 결선 완료', '운전실 전장기기 취부 결선(TC)'],
#     'C': ['흡음재 취부', '흡음재 씰링/검사/수정', '측창취부/T-BOLT 삽입', '실내/상하 CABLE HARNESS 취부', '실내/상하 배선',
#           '실내 배선 작업', '객실도어 취부', '객실도어 취부 검사', '하부덕트검사\n (D+1~4일차 조정작업)', 'CAB MODULE 취부(TC)',
#           '배전반 취부 및 배선작업', '운전실 내장판 취부', '운전실 캐비넷 취부(TC)', '운전실 배전반 결선(TC)', '운전실 DOOR 취부(TC)',
#           '도통검사(량단위 시험기)', '도통 자체 검사(완료)', '도통 검사 수정', '도통입회검사/내전압자체검사', '내전압 입회검사',
#           '수정작업 및 점검커버 복구', 'D+17~20일차 조정작업', '전장취부, 결선 복구 완료', '실내 조정 및 실내·외 설비 완료',
#           '전장품 취부 입회검사', '복구 및 수정작업', '실내 설비 입회검사', '대차차입 전검사 / 대차차입', '대차 전장품 취부 결선 & 마무리', '대차차입 후 검사']
# }
# #
# print(list(df_data.index.drop_duplicates()) == process_list)
# max_index_dict = {}
# for key, sub_list in process_dict.items():
#     indices = [process_list.index(item) for item in sub_list if item in process_list]
#     print(key, indices == sorted(indices))
#     print(indices)
#     print(sub_list)
#     max_index_dict[key] = max(indices)
#
# max_index = sorted(max_index_dict.values())[-2] + 1
# max_key = [key for key in max_index_dict if max_index_dict[key] == sorted(max_index_dict.values())[-1]][0]
# print(max_key, max_index)
#
# process_dict['D'] = process_dict[max_key][process_dict[max_key].index(process_list[max_index]):]
# process_dict[max_key] = process_dict[max_key][:process_dict[max_key].index(process_list[max_index])]
#
# indices_dict = {
#     key: [process_list.index(item) for item in sub_list if item in process_list]
#     for key, sub_list in process_dict.items()
# }

# for name, subway_car in subway_car_dict.items():
#     subway_car.min_index_dict = dict.fromkeys(process_dict.keys(), None)
#     subway_car.min_date_index = process_list.index(min(subway_car.activity_dict.items(), key=lambda item: item[1])[0])
#     for activity_name, date in subway_car.activity_dict.items():
#         index = process_list.index(activity_name)
#         for key in indices_dict:
#             if index in indices_dict[key]:
#                 if subway_car.min_index_dict[key] is None or subway_car.min_index_dict[key] > index:
#                     subway_car.min_index_dict[key] = index
#
#     print(name, subway_car.min_date_index, subway_car.min_index_dict, subway_car.min_date_index == min(filter(lambda x: x is not None, subway_car.min_index_dict.values())))
# # 가장 작은 값은 optional=False 로 해야겠네
# print(len(list(subway_car_dict.keys())))
# #일단 33 34 35 다음인 36부터가 전체 공정인듯


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

for name, subway_car in subway_car_dict.items():
    temp_name_date = []
    for process in process_list:
        if process not in subway_car.activity_dict:
            continue
        activity_name = process
        date = subway_car.activity_dict[activity_name]
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

# 결론 2: result1에서 except_list2와 2번 이상 어긋난 항목 제외
final_result2 = sorted(list(set(result1) - set(except_list2)))

# 결론 3: result2에서 except_list1과 2번 이상 어긋난 항목 제외
final_result3 = sorted(list(set(result2) - set(except_list1)))

# final_result = final_result1

# print([item for item in final_result if 6 not in item and 8 not in item])
# edges1 = [item for item in final_result if 6 not in item and 8 not in item]
# edges2 = [item for item in final_result if 6 in item or 8 in item]
# edges = [item for item in final_result if 6 == item[1] or 8 == item[1]]
edges1 = [item for item in final_result1]
edges2 = [item for item in final_result2]
edges3 = [item for item in final_result3]
# print([item for item in final_result2 if 6 not in item and 8 not in item])


# 그래프 생성
G = nx.DiGraph()  # 유향 그래프
G.add_edges_from(edges1)

# 1. 이어지는 관계 확인 (Connected Components)
connected_components = list(nx.weakly_connected_components(G))  # 약 연결 컴포넌트
print("이어지는 관계 (연결된 컴포넌트):", connected_components)

print('---------------------------')

# 그래프 생성
G = nx.DiGraph()  # 유향 그래프
G.add_edges_from(edges2)

# 1. 이어지는 관계 확인 (Connected Components)
connected_components = list(nx.weakly_connected_components(G))  # 약 연결 컴포넌트
print("이어지는 관계 (연결된 컴포넌트):", connected_components)

print('---------------------------')

# 그래프 생성
G = nx.DiGraph()  # 유향 그래프
G.add_edges_from(edges3)

# 1. 이어지는 관계 확인 (Connected Components)
connected_components = list(nx.weakly_connected_components(G))  # 약 연결 컴포넌트
print("이어지는 관계 (연결된 컴포넌트):", connected_components)