import networkx as nx
from networkx.drawing.nx_pydot import pydot_layout
import matplotlib.pyplot as plt
import os
from get_data import *

def plot_network(self):
    data_proc4 = load_api(self, 'Processes/Seq?pcCd=PROC0004')
    df_proc4 = pd.DataFrame(data_proc4['data'])
    df_proc4['pc'] = (df_proc4.index + 1).astype(str)

    data = list(df_proc4[['pc', 'pcTp', 'examCheck']].itertuples(index=False, name=None))

    stops_idxs = [i for i, (_, _, exam) in enumerate(data) if exam == 1]

    edges = []

    first_stop_idx = stops_idxs[0]
    first_stop = data[first_stop_idx][0]
    initial = [pc for pc, _, _ in data[:first_stop_idx]]

    if len(initial) == 0:
        edges.append((data[0][0], first_stop))

    elif len(initial) == 1:
        act = initial[0]
        edges.append((act[0], first_stop))

    else:
        groups = {}
        for pc, pctp, exam in data[:first_stop_idx]:
            groups.setdefault(pc, []).append(pc)
        for same in groups.values():
            edges.append((data[0][0], same[0]))
            for u, v in zip(same, same[1:]):
                edges.append((u, v))
            edges.append((same[-1], first_stop))

    for pre_idx, next_idx in zip(stops_idxs, stops_idxs[1:]):
        pre_stop = data[pre_idx][0]
        next_stop = data[next_idx][0]
        segment = data[pre_idx + 1: next_idx]
        pcs = [pc for pc, _, _ in segment]
        tps = [tp for _, tp, _ in segment]

        if len(segment) == 0:
            edges.append((pre_stop, next_stop))

        elif len(segment) == 1 or len(set(tps)) == 1:
            act = pcs[0]
            edges.append((pre_stop, act))
            for u, v in zip(pcs, pcs[1:]):
                edges.append((u, v))
            edges.append((pcs[-1], next_stop))

        else:
            groups = {}
            for pc, pctp, _ in segment:
                groups.setdefault(pctp, []).append(pc)  # {1:['1','2'], 2:['3']}

            for same in groups.values():
                edges.append((pre_stop, same[0]))
                for u, v in zip(same, same[1:]):
                    edges.append((u, v))
                edges.append((same[-1], next_stop))

    last_stop_idx = stops_idxs[-1]
    last_stop = data[last_stop_idx][0]
    final = [pc for pc, _, _ in data[last_stop_idx + 1:]]

    if len(final) == 1 or len({pctp for _, pctp, _ in data[last_stop_idx + 1:]}) == 1:
        edges.append((last_stop, final[0]))
        for u, v in zip(final, final[1:]):
            edges.append((u, v))

    elif len(final) > 1:
        groups = {}
        for pc, pctp, exam in data[last_stop_idx + 1:]:
            groups.setdefault(pctp, []).append(pc)
        for same in groups.values():
            edges.append((last_stop, same[0]))
            for u, v in zip(same, same[1:]):
                edges.append((u, v))

    G = nx.MultiDiGraph()
    for pc, pctp, exam in data:
        G.add_node(pc, pcTp=pctp, examCheck=exam)
    G.add_edges_from(edges)

    colors = {}
    for pc, pctp, exam in data:
        if exam == 1:
            colors[pc] = "pink"
        elif pctp == 1:
            colors[pc] = "lightblue"
        elif pctp == 2:
            colors[pc] = "lightgreen"
        elif pctp == 3:
            colors[pc] = "yellow"

    node_colors = [colors[n] for n in G.nodes()]

    pos = pydot_layout(G, prog='dot')
    pos = {n: (-y, x) for n, (x, y) in pos.items()}

    plt.figure(figsize=(17, 2))
    nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, edgecolors='black', linewidths=1.2)
    nx.draw_networkx_labels(G, pos, font_size=7, font_weight='bold')
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10, width=1.2)

    plt.axis('off')
    plt.tight_layout()

    # results_dir = Path(__file__).resolve().parent
    # results_dir = results_dir / 'results'
    # results_dir.mkdir(exist_ok=True)

    result_path = os.path.join(self.config['folderpath'], 'Activity_Network_57.png')
    plt.savefig(result_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[saved to: {result_path}]")

    #### 차량별 액티비티 네트워크 ####
    G_full = G.copy()
    pos_full = pos
    date_range = list(pd.date_range(start=self.start_time, end=self.end_time, freq='D'))
    day_to_index_calendar_dict = {date: i for i, date in enumerate(date_range)}

    vehicle_dict = {}  # 차량 아이디: 공정분류 명
    plan_date = {}  # 차량 아이디: (공정 이름: 날짜)

    df_vehicle = pd.DataFrame(load_api(self, 'Cars/e672bd1e-5ed0-4baa-9cbd-50db20ea24db?allYn=Y')['data'])
    for i, row in df_vehicle.iterrows():
        data_temp = load_api(self, 'WorkPlan/e672bd1e-5ed0-4baa-9cbd-50db20ea24db?carId=' + row['carId'])
        if data_temp['code'] == 10:
            continue
        df_temp = pd.DataFrame(data_temp['data'])
        df_temp = df_temp[pd.to_datetime(df_temp['planDate']) >= self.start_time]
        df_temp = df_temp[pd.to_datetime(df_temp['planDate']) <= self.end_time]
        df_temp = df_temp[df_temp['pcId'].isin(df_proc4['pcId'])]
        if df_temp.shape[0] == 0:
            continue
        vehicle_dict[row['carCd']] = list(df_temp['pcNm'])
        df_temp['day_idx'] = df_temp['planDate'].map(day_to_index_calendar_dict)
        plan_date[row['carCd']] = {str(pc): int(date) for pc, date in zip(df_temp['pcNm'], df_temp['day_idx'])}

    for vehicle_name, operations in vehicle_dict.items():
        data = []
        edges = []
        G = nx.MultiDiGraph()
        for operation in operations:
            sub = df_proc4.loc[df_proc4['pcNm'] == operation, ['pc', 'pcTp', 'examCheck']]
            operation_data = list(sub.itertuples(index=False, name=None))
            data.extend(operation_data)

    def node_color_for(attrs):
        if attrs.get('examCheck', 0) == 1:
            return 'pink'
        tp = attrs.get('pcTp')
        return {1: 'lightblue', 2: 'lightgreen', 3: 'yellow'}.get(tp, 'lightgray')

    pc_to_pcNm = dict(df_proc4[['pc', 'pcNm']].values)

    for vehicle_name, operations in list(vehicle_dict.items()):
        raw = []
        for operation in operations:
            sub = df_proc4.loc[df_proc4['pcNm'] == operation, ['pc', 'pcTp', 'examCheck']]
            operation_data = list(sub.itertuples(index=False, name=None))
            raw.extend(operation_data)

        remain = {str(pc) for pc, _, _ in raw if str(pc) in G_full.nodes()}

        labels = {}
        pcNm_dayidx = plan_date.get(vehicle_name, {})
        for pc in remain:
            name = pc_to_pcNm[pc]
            idx = pcNm_dayidx[name]
            if idx is not None:
                labels[pc] = idx
            else:
                labels[pc] = None

        plt.figure(figsize=(17, 2))
        nx.draw_networkx_edges(G_full, pos_full, width=1.2, arrows=False)
        nx.draw_networkx_nodes(G_full, pos_full, node_size=200, node_color='lightgray', edgecolors='none')

        remain_colors = [node_color_for(G_full.nodes[n]) for n in remain]
        nx.draw_networkx_nodes(G_full, pos_full, nodelist=list(remain), node_size=220, node_color=remain_colors,
                               edgecolors='black', linewidths=1.2)
        nx.draw_networkx_labels(G_full, pos_full, labels=labels, font_size=7, font_weight='bold')

        remain_edges = [(u, v) for (u, v) in G_full.edges() if u in remain and v in remain]
        nx.draw_networkx_edges(G_full, pos_full, edgelist=remain_edges, width=1.2, arrowstyle='->', arrowsize=10)

        plt.title(f"Vehicle {vehicle_name}")
        plt.axis('off')
        plt.tight_layout()

        sub_dir = os.path.join(self.config['folderpath'], "vehicles")
        os.makedirs(sub_dir, exist_ok=True)
        sub_path = os.path.join(sub_dir, f"Activity_Network_57_of_Vehicle: {vehicle_name}.png")
        plt.savefig(sub_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[saved to: {sub_path}]")

