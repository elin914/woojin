import networkx as nx
from networkx.drawing.nx_pydot import pydot_layout
import matplotlib.pyplot as plt
import os
from get_data import *
from class_definition import *

def plot_network(self):
    data = []
    for operation_name, operation in self.operation_dict.items():
        pc = operation_name
        pctp = operation.department
        examchek = operation.test_operation
        data.append((pc, pctp, examchek))


    # data_proc4 = load_api(self, 'Processes/Seq?pcCd=PROC0004')
    # df_proc4 = pd.DataFrame(data_proc4['data'])
    # df_proc4['pc'] = (df_proc4.index + 1).astype(str)
    #
    # data = list(df_proc4[['pc', 'pcTp', 'examCheck']].itertuples(index=False, name=None))

    stops_idxs = [i for i, (_, _, exam) in enumerate(data) if exam == 1]

    edges = []

    first_stop_idx = stops_idxs[0]
    first_stop = data[first_stop_idx][0]
    initial = [pc for pc, _, _ in data[:first_stop_idx]]

    if len(initial) == 0:
        edges.append((data[0][0], first_stop))

    elif len(initial) == 1:
        act = initial[0]
        edges.append((act, first_stop))

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

    def make_color_from_grapgh(G):
        def color_for(n: str) -> str:
            attrs = G.nodes[n]
            exam = attrs.get('examCheck', 0)
            pctp = attrs.get('pcTp', 0) or 0
            try:
                pctp = int(pctp)
            except (TypeError, ValueError):
                pctp = 0

            if exam == 1:
                return "pink"
            elif pctp == 1:
                return "lightblue"
            elif pctp == 2:
                return "lightgreen"
            elif pctp == 3:
                return "yellow"
            return "red"
        return color_for

    color_for = make_color_from_grapgh(G)
    colors = {n: color_for(n) for n in G.nodes()}
    node_colors = [colors[n] for n in G.nodes()]

    pos = pydot_layout(G, prog='dot')
    pos = {n: (-y, x) for n, (x, y) in pos.items()}

    labels = {n: n.replace("operation", "") for n in G.nodes()}

    plt.figure(figsize=(17, 2))
    nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, edgecolors='black', linewidths=1.2)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, font_weight='bold')
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
    plan_date = {}  # 차량 아이디: {공정 이름: 날짜}

    for vehicle_name, vehicle in self.vehicle_dict.items():
        vehicle_dict[vehicle_name] = vehicle.operation_list
        plan_date[vehicle_name] = vehicle.operation_dict

        data_sub = []
        G = nx.MultiDiGraph()
        for operation in vehicle.operation_list:
            pc_sub = operation
            pctp_sub = self.operation_dict[operation].department
            examcheck_sub = self.operation_dict[operation].test_operation
            data_sub.append((pc_sub, pctp_sub, examcheck_sub))

        remain = {str(pc) for pc, _, _ in data_sub if str(pc) in G_full.nodes()}

        labels_sub = {n: plan_date[vehicle_name][n] for n in remain}


        plt.figure(figsize=(17, 2))
        nx.draw_networkx_edges(G_full, pos_full, width=1.2, arrows=False)
        nx.draw_networkx_nodes(G_full, pos_full, node_size=200, node_color='lightgray', edgecolors='none')

        color_for = make_color_from_grapgh(G_full)
        remain_colors = [color_for(n) for n in remain]
        nx.draw_networkx_nodes(G_full, pos_full, node_size=220, node_color='lightgray',
                               edgecolors='black', linewidths=1.2)
        nx.draw_networkx_nodes(G_full, pos_full, nodelist=list(remain), node_size=220, node_color=remain_colors,
                               edgecolors='black', linewidths=1.2)
        nx.draw_networkx_labels(G_full, pos_full, labels=labels_sub, font_size=7, font_weight='bold')

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

