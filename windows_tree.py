import sys

import pandas as pd
from anytree import Node, RenderTree
import anytree

import os
import tempfile

if getattr(sys, 'frozen', False):
    executable_path = os.path.dirname(sys.executable)
else:
    executable_path = os.path.dirname(os.path.abspath(__file__))

UTIL_FOLDER = f'{executable_path}/utils/'
PROCMON = f'{UTIL_FOLDER}/Procmon64.exe /AcceptEula /Quiet /Minimized'


def run_save_csv(input_filename: str, temp_path: str):
    os.system(
        f'{PROCMON} /LoadConfig "{UTIL_FOLDER}/ProcmonConfiguration.pmc" /OpenLog "{input_filename}" /SaveApplyFilter /SaveAs "{temp_path}"')


def parse_tree(df):
    nodes = {}

    for _, row in df.iterrows():
        if row['Operation'] == 'Process Create' and row['Result'] == 'SUCCESS':
            try:
                parent_pid = int(row['PID'])
                parent_name = row['Process Name']

                detail = row['Detail']
                if 'PID: ' in detail:
                    pid = int(detail.split('PID: ')[1].split(',')[0])
                else:
                    continue

                # Имя дочернего процесса берем из колонки Path
                process_name = row['Path'].split('\\')[-1]

                # Создаем родительский узел, если его еще нет
                if parent_pid not in nodes:
                    nodes[parent_pid] = Node(f"{parent_name} (PID: {parent_pid})")

                # Создаем дочерний узел
                if pid not in nodes:
                    nodes[pid] = Node(f"{process_name} (PID: {pid})", parent=nodes[parent_pid])

            except (ValueError, IndexError, AttributeError) as e:
                print(f"Warning: Could not parse line for PID {row['PID']}: {e}")
                continue

    # Находим корневые узлы (узлы без родителей)
    root_nodes = [node for node in nodes.values() if node.parent is None]
    return root_nodes


def make_tree(path: str) -> None:
    tmp_csv_file_path = str()

    try:
        tmp_csv_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_csv_file_path = tmp_csv_file.name + ".csv"
        print(tmp_csv_file_path)
        tmp_csv_file.close()

        run_save_csv(path, tmp_csv_file_path)
        df = pd.read_csv(tmp_csv_file_path)

        roots = parse_tree(df)

        for root in roots:
            for pre, _, node in RenderTree(root, style=anytree.render.ContStyle()):
                print(f"{pre}{node.name}")

    except FileNotFoundError:
        print("Error: Logfile.CSV not found")

    os.remove(tmp_csv_file_path)
