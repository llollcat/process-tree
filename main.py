import sys
import tkinter as tk
from tkinter import filedialog

import macos_tree
import windows_tree
import linux_tree

LINUX = 'Trace_new_processes_via_exec_syscalls_for_tree.txt'
LINUX_BCC = 'Trace_new_processes_via_exec_syscalls.txt'
MACOS = 'pstree_trace.txt'
WINDOWS = '.PML'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Выберите файл трассировки")
        if not path:
            sys.exit(1)
    else:
        path = sys.argv[1]

    if LINUX in path:
        print('Linux')
        linux_tree.make_tree(path)
    elif LINUX_BCC in path:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            f.close()
        if first_line.startswith("PCOMM"):
            print('Linux (BCC)')
            linux_tree.make_tree(path)
        else:
            print("Файл не является результатом работы BCC Trace")
    elif MACOS in path:
        print('Mac OS')
        macos_tree.make_tree(path)
    elif path.endswith(WINDOWS):
        print('Windows')
        windows_tree.make_tree(path)
    else:
        print('Формат не определён')

    input("Для продолжения нажмите Enter...")
