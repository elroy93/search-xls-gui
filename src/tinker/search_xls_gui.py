import json
import os
import pickle
import re
import subprocess
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog
from tkinter import ttk

import prettytable as pt
import pythoncom
import win32com.client as win32
from prettytable import PrettyTable, NONE

# 表头定义
TABLE_HEADER_INDEX = 'Index'
TABLE_HEADER_PATH = 'Path'
TABLE_HEADER_SHEET = 'Sheet'
TABLE_HEADER_CELL = 'Cell'
TABLE_HEADER_VALUE = 'Value'
TABLE_COLUMNS = (TABLE_HEADER_INDEX, TABLE_HEADER_PATH, TABLE_HEADER_SHEET, TABLE_HEADER_CELL, TABLE_HEADER_VALUE)
TABLE_COLUMN_INDICES = {name: index for index, name in enumerate(TABLE_COLUMNS)}

TABLE_TAG_MARKED = 'marked'

# 配置文件
search_xls_store_file = "search_xls_store.pkl"


@dataclass
class FoundCell:
    index: int
    path: str
    sheet: str
    cell: object
    cell_value: object = None

    def __init__(self, index, path, sheet, cell, cell_value):
        self.index = index
        self.path = path
        self.sheet = sheet
        self.cell = cell
        self.cell_value = cell_value


@dataclass
class FileStore:
    folder_path: str
    search_txt: str
    file_filter: str = ""
    is_strict: int = 0
    match_case: int = 0


file_store = FileStore("", "")
global_excel = None
search_thread = None

# 创建一个Event对象
stop_event = threading.Event()


def global_excel_quit():
    global global_excel
    if global_excel:
        try:
            global_excel.Quit()
        except:
            pass
        finally:
            global_excel = None


def console_print(msg):
    print(" >>>> " + msg)
    global search_thread
    if search_thread:
        search_thread.join

    def _print():
        console_output.insert(tk.END, msg + "\n")
        console_output.see(tk.END)

    global stop_event
    if not stop_event.is_set():
        app.after(0, _print)


def select_path():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return
    path_entry.delete(0, tk.END)  # Clear the text field
    path_entry.insert(0, folder_path)  # Insert the selected path


def add_to_tree(found_cell):
    def _add():
        tree.insert('', 'end', values=(
            found_cell.index, found_cell.path, found_cell.sheet, found_cell.cell, found_cell.cell_value))

    app.after(0, _add)


# 打开文件
def open_file(path):
    os.startfile(path)


# 打开文件夹
def open_folder_and_selected(path):
    subprocess.Popen(f'explorer /select,"{path}"')


# 标注
def toggle_mark_row():
    for selected_item in tree.selection():
        tags = list(tree.item(selected_item, 'tags'))
        if not (TABLE_TAG_MARKED in tags):
            tags.append(TABLE_TAG_MARKED)
            tree.item(selected_item, tags=tags)


# 取消标注
def toggle_unmark_row():
    for selected_item in tree.selection():
        tags = list(tree.item(selected_item, 'tags'))
        if TABLE_TAG_MARKED in tags:
            tags.remove(TABLE_TAG_MARKED)
            tree.item(selected_item, tags=tags)


# 右键点击事件
def on_column_right_click(event):
    # 获取选中的行
    selected_item = tree.selection()[0]
    # 获取选中行的文件路径
    file_path = tree.item(selected_item, "values")[TABLE_COLUMN_INDICES[TABLE_HEADER_PATH]]
    console_print("右键点击 : " + file_path)
    # 创建一个弹出菜单
    menu = tk.Menu(app, tearoff=0)
    menu.add_command(label="打开文件", command=lambda: open_file(file_path))
    menu.add_command(label="打开文件夹", command=lambda: open_folder_and_selected(file_path))
    # 获取选中的行的所有标签
    if TABLE_TAG_MARKED in list(tree.item(selected_item, 'tags')):
        menu.add_command(label="取消标注", command=toggle_unmark_row)  # 添加标注/取消标注选项
    else:
        menu.add_command(label="标注", command=toggle_mark_row)  # 添加标注/取消标注选项
    menu.add_command(label="复制", command=copy_to_clipboard)  # 添加复制选项

    # 显示弹出菜单
    menu.post(event.x_root, event.y_root)


# 复制选中内容到剪贴板
def copy_to_clipboard():
    table = PrettyTable(TABLE_COLUMNS, hrules=NONE)
    table.set_style(pt.PLAIN_COLUMNS)
    table.align = "l"
    # 获取选中的行
    selected_items = tree.selection()
    for selected_item in selected_items:
        # 获取选中行的内容
        item_values = tree.item(selected_item, "values")
        # 将选中行的内容添加到表格中
        table.add_row(item_values)

    print(table)
    # 将内容复制到剪贴板
    app.clipboard_clear()
    app.clipboard_append((str(table)))


def search(input_stop_event):
    # 初始化COM库
    pythoncom.CoInitialize()

    search_text = search_key_entry.get().strip()
    win_folder_path = path_entry.get()
    is_strict = strict_equal_entry.get()
    match_case = match_case_entry.get()
    file_filter = file_filter_entry.get().strip()

    # 保存设置选项
    if True:
        file_store.folder_path = win_folder_path
        file_store.search_txt = search_text
        file_store.is_strict = is_strict
        file_store.match_case = match_case
        file_store.file_filter = file_filter

        store_content_json_str = json.dumps(file_store.__dict__)
        with open(search_xls_store_file, 'wb') as config_store:
            pickle.dump(store_content_json_str, config_store)
            console_print("保存设置选项 : " + store_content_json_str)

    folder_path = win_folder_path.replace("/", "\\")

    search_file_in_dir(input_stop_event, search_text, folder_path, is_strict > 0, match_case > 0, file_filter)
    global_excel_quit()
    pythoncom.CoUninitialize()


def search_in_thread():
    # 清空表格
    tree.delete(*tree.get_children())
    # 清空控制台
    console_output.delete('1.0', tk.END)

    global stop_event
    global search_thread
    search_thread = threading.Thread(target=search, args=(stop_event,))
    search_thread.setDaemon(True)
    search_thread.start()
    # 关闭线程


def get_all_files_recursively_xls(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # ~$
            if file.startswith("~$"):
                continue
            if file.endswith(".xlsx") or file.endswith(".xls"):
                yield os.path.join(root, file)


def search_file_in_dir(input_stop_event,
                       search_text,
                       folder_path,
                       is_strict=False,
                       match_case=False,
                       file_filter_regex: str = ""):
    # 启动Excel应用程序
    excel = win32.Dispatch('Excel.Application')
    global global_excel
    global_excel = excel
    # 设置Excel为后台运行
    excel.Visible = False
    excel.ScreenUpdating = False
    excel.DisplayAlerts = False
    excel.EnableEvents = False
    excel.Interactive = False
    # 取消excel的警告
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False

    console_print("\n开始搜索 ... ")
    search_text = search_text.strip()
    index = 0
    found_list = []
    files = []
    if os.path.isfile(folder_path):
        files.append(folder_path)
    else:
        files = list(get_all_files_recursively_xls(folder_path))
    # 如果有过滤条件, 使用正则表达式过滤
    if file_filter_regex:
        files = [f for f in files if re.search(file_filter_regex, f)]

    # 遍历文件夹中的所有xlsx文件
    for file_name in files:
        if input_stop_event.is_set():
            global_excel_quit()
            return

        index += 1
        start_time = time.time_ns()
        file_path = os.path.join(folder_path, file_name)
        try:
            # 打开一个现有的工作簿
            workbook = excel.Workbooks.Open(file_path)
            # 如果 search_text 是空的
            if len(search_text) > 0:
                for sheet in workbook.Sheets:
                    if input_stop_event.is_set():
                        global_excel_quit()
                        return
                    first_cell = sheet.Cells.Find(What=search_text)
                    if first_cell is not None:
                        cell = first_cell
                        while True:
                            match_strict_success = (is_strict is False or str(cell.Value).strip() == search_text)
                            match_case_success = (match_case is False or search_text in str(cell.Value))
                            if match_strict_success and match_case_success:
                                msg = f"\t {search_text} : {file_path} {sheet.Name} - {cell.Address}"
                                console_print(msg)
                                found_list.append(msg)
                                add_to_tree(
                                    FoundCell(len(found_list),
                                              file_path,
                                              sheet.Name,
                                              str(cell.Address),
                                              str(cell.Value)))
                            cell = sheet.Cells.FindNext(cell)
                            if not cell or cell.Address == first_cell.Address:
                                break
                workbook.Close(False)
            else :
                # 如果 search_text 是空的, 则是搜索文件
                found_list.append(f"找到文件 : {file_path}")
                add_to_tree(
                    FoundCell(len(found_list),
                              file_path,
                              "",
                              "",
                              ""))
                pass
        except:
            console_print("Error in file : " + file_name)
            continue
        finally:
            end_time = time.time_ns()
            console_print(
                f"({index}/{len(files)}) searching {search_text} in : {file_path} , cost={(end_time - start_time) // 1000_1000}ms")
        pass
    # 退出Excel
    excel.Quit()

    console_print("")
    console_print("")
    console_print(f" ------ search {search_text} in {folder_path}, total {len(found_list)} ------ ")
    console_print("")
    for found in found_list:
        console_print(found)

    console_print("")
    console_print("")
    console_print(" ************************************* ")
    console_print(" *                                   * ")
    console_print(" *          search finished !        * ")
    console_print(" *                                   * ")
    console_print(" ************************************* ")


def on_closing():
    # 设置停止标志
    console_print("正在退出 ... ")
    global stop_event
    stop_event.set()
    global_excel_quit()
    app.destroy()
    console_print("退出完成 ... ")


if __name__ == '__main__':

    app = tk.Tk()
    app.title("excel内容搜索工具 - by elroysu")

    # 获取屏幕宽度和高度
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    # 设置窗口大小和位置
    window_width = int(screen_width / 2)
    window_height = int(screen_height / 2)
    x_position = int(screen_width / 2 - window_width / 2)
    y_position = int(screen_height / 2 - window_height / 2)
    app.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')

    # 第一行
    path_label = tk.Label(app, text="选择目录 :")
    path_label.grid(row=0, column=0)
    path_entry = tk.Entry(app)
    path_entry.grid(row=0, column=1, sticky='ew')
    path_button = tk.Button(app, text="打开", command=select_path, bg='#bae0ff')
    path_button.grid(row=0, column=2)

    # 第二行
    file_filter_label = tk.Label(app, text="文件过滤 :")
    file_filter_label.grid(row=1, column=0)
    file_filter_entry = tk.Entry(app)
    file_filter_entry.grid(row=1, column=1, sticky='ew')

    # 第3行
    label = tk.Label(app, text="搜索内容 :")
    label.grid(row=2, column=0)
    search_key_entry = tk.Entry(app)
    search_key_entry.grid(row=2, column=1, sticky='ew')
    search_button = tk.Button(app, text="搜索", command=search_in_thread, bg='#bae0ff')
    search_button.grid(row=2, column=2)

    # 第4行
    frame = tk.Frame(app, bg='black', padx=1, pady=1)
    frame.grid(row=3, column=0, columnspan=3)
    # 严格模式
    strict_equal_entry = tk.IntVar()
    strict_equal_checkbutton = tk.Checkbutton(frame, text="严格模式", variable=strict_equal_entry)
    strict_equal_checkbutton.grid(row=0, column=1)
    # 匹配大小写
    match_case_entry = tk.IntVar()
    match_case_checkbutton = tk.Checkbutton(frame, text="匹配大小写", variable=match_case_entry)
    match_case_checkbutton.grid(row=0, column=2)

    # 第四行
    # Create Treeview
    tree = ttk.Treeview(app, columns=TABLE_COLUMNS, show='headings')
    tree.heading(TABLE_HEADER_INDEX, text=TABLE_HEADER_INDEX)
    tree.heading(TABLE_HEADER_PATH, text=TABLE_HEADER_PATH)
    tree.heading(TABLE_HEADER_SHEET, text=TABLE_HEADER_SHEET)
    tree.heading(TABLE_HEADER_CELL, text=TABLE_HEADER_CELL)
    tree.heading(TABLE_HEADER_VALUE, text=TABLE_HEADER_VALUE)
    tree.column(TABLE_HEADER_INDEX, width=10)
    tree.column(TABLE_HEADER_PATH, width=500)
    tree.column(TABLE_HEADER_SHEET, width=100)
    tree.column(TABLE_HEADER_CELL, width=100)
    tree.column(TABLE_HEADER_VALUE, width=100)
    # tree.grid(row=2, column=0, columnspan=3, sticky='nsew')
    tree.bind("<Button-3>", on_column_right_click)
    tree.bind("<Control-c>", lambda e: copy_to_clipboard())
    tree.tag_configure(TABLE_TAG_MARKED, background='yellow')  # 配置标签的样式
    # Create a vertical scrollbar
    vsb = ttk.Scrollbar(app, orient="vertical", command=tree.yview)
    vsb.grid(row=4, column=2, sticky='ns')  # Change column from 3 to 2

    # Configure the treeview to use the scrollbar
    tree.configure(yscrollcommand=vsb.set)

    tree.grid(row=4, column=0, columnspan=2, sticky='nsew')

    # 第五行, 控制台
    console_output = tk.Text(app, height=10)
    console_output.grid(row=5, column=0, columnspan=3, sticky='nsew')

    # Configure the grid to expand
    app.grid_rowconfigure(2)
    app.grid_rowconfigure(3, weight=0)
    app.grid_rowconfigure(4, weight=1)
    app.grid_columnconfigure(1, weight=1)

    # Make the window resizable
    app.resizable(True, True)

    # Load the last selected directory
    if os.path.exists(search_xls_store_file):
        read_exception = False
        with open(search_xls_store_file, 'rb') as f:
            try:
                # print(" >>>> " +pickle.load(f))
                file_store_json = json.loads(pickle.load(f))
                # # json转对象
                file_store = FileStore(**file_store_json)
                path_entry.insert(0, file_store.folder_path)
                search_key_entry.insert(0, file_store.search_txt)
                file_filter_entry.insert(0, file_store.file_filter)
                strict_equal_entry.set(file_store.is_strict)
                match_case_entry.set(file_store.match_case)
                console_print("上次目录 : " + file_store.folder_path)
                console_print("上次搜索 : " + file_store.search_txt)
            except:
                # 删除之前的配置文件
                read_exception = True
        if read_exception:
            os.remove(search_xls_store_file)

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

# if __name__ == '__main__':
#     search_text = r"moveSpeed"
#     folder_path = r"D:\aoem\aoem-trunk\server\NewKing\common\common\excel\xls\Main"
#     search_file_in_dir(search_text, folder_path)
