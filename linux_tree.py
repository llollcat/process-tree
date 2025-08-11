from anytree import Node, RenderTree
from collections import defaultdict


def parse_line(line):
    # Минимум 4 первых поля: PCOMM, PID, PPID, RET
    parts = line.strip().split(maxsplit=4)
    if len(parts) < 4:
        return None

    # PCOMM может быть обрезан до 15 символов
    comm = parts[0]
    pid = parts[1]
    ppid = parts[2]
    return comm, pid, ppid

def build_process_tree(input_lines):
    nodes = {}
    tree_data = defaultdict(list)

    for line in input_lines:
        if not line.strip() or line.startswith("PCOMM"):
            continue

        parsed = parse_line(line)
        if not parsed:
            continue

        comm, pid, ppid = parsed

        if pid not in nodes:
            nodes[pid] = Node(f"{comm} (PID: {pid})")
            tree_data[ppid].append(pid)

    # Строим связи между узлами
    for ppid, child_pids in tree_data.items():
        if ppid in nodes:
            parent_node = nodes[ppid]
            for child_pid in child_pids:
                if child_pid in nodes:
                    nodes[child_pid].parent = parent_node

    return nodes




def make_tree(path: str) -> None:
    with open(path, 'r') as f:
        lines = f.readlines()

    nodes = build_process_tree(lines)

    # Отображаем корневые процессы (у которых нет родителя)
    root_nodes = [node for pid, node in nodes.items() if not node.parent]

    for root in root_nodes:
        for pre, _, node in RenderTree(root):
            print(f"{pre}{node.name}")
