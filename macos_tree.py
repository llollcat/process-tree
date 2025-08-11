from anytree import Node, RenderTree
from collections import defaultdict

import re


def parse_process_line(line):
    match = re.search(r'(\d+)\s+(\w+)\s+(\/.+)', line)
    if match:
        pid = match.group(1)
        user = match.group(2)
        cmd = match.group(3).split()[0]  # только путь к исполняемому файлу
        procname = cmd.split('/')[-1]
        return pid, f"{procname} (PID: {pid})"
    return None, None


def parse_tree(lines):
    all_nodes = {}
    pid_tree = defaultdict(list)
    root_pids = set()
    indent_levels = {}

    current_root_pid = None

    for line in lines:
        line = line.rstrip()
        if re.fullmatch(r'\d+', line):  # строка только с PID
            current_root_pid = line
            root_pids.add(current_root_pid)
            continue

        # определим уровень отступа
        indent_match = re.match(r'^([|\\\-\+ ]+)', line)
        indent_level = len(indent_match.group(1)) if indent_match else 0

        # парсим строку процесса
        proc_line_match = re.search(r'(\d{5})\s+\w+\s+/.+', line)
        if proc_line_match:
            pid, label = parse_process_line(line)
            if pid:
                node = Node(label)
                all_nodes[pid] = node
                pid_tree[current_root_pid].append((pid, indent_level))
                indent_levels[pid] = indent_level

    # строим общее дерево
    launchd_node = Node("launchd (PID: 00001)")
    all_nodes["00001"] = launchd_node

    # собираем все процессы и их родителей
    parent_map = {}
    for root_pid, entries in pid_tree.items():
        entries.sort(key=lambda x: x[1])  # сортируем по уровню отступа

        stack = []
        for pid, level in entries:
            while stack and indent_levels[stack[-1][0]] >= level:
                stack.pop()

            if stack:
                parent_pid = stack[-1][0]
                parent_map[pid] = parent_pid
            else:
                parent_map[pid] = "00001"  # родитель - launchd

            stack.append((pid, level))

    # создаем узлы и связываем их
    for pid, node in all_nodes.items():
        if pid == "00001":
            continue

        parent_pid = parent_map.get(pid)
        if parent_pid and parent_pid in all_nodes:
            node.parent = all_nodes[parent_pid]
        else:
            node.parent = launchd_node

    return launchd_node


def make_tree(path: str) -> None:
    with open(path, "r") as f:
        lines = f.readlines()

    root_node = parse_tree(lines)

    for pre, _, node in RenderTree(root_node):
        print(f"{pre}{node.name}")