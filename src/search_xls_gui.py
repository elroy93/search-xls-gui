import ctypes
import os
import pickle
import queue
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Generator

import pythoncom
import win32com.client as win32
from PySide6.QtCore import QThread
from PySide6.QtCore import QUrl
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDesktopServices, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QWidget,
    QPushButton,
    QStyle,
)
from PySide6.QtWidgets import QMenu

from src.ui.ui_search_widget import Ui_search_widget
from ui.ui_main import Ui_MainWindow
from utils import get_all_files_recursively_xls, cell_value_match, get_icon

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("starter")

search_xls_store_file = ".search_xls_gui_store.pkl"


class SearchThread(QThread):
    def __init__(self, window, params, queue: queue.Queue):
        QThread.__init__(self)
        self.window = window
        self.params = params
        self.q = queue

    def run(self):
        # self.window.emit_log("new thread start search")
        # self.window.do_search_xlwings(self.params)
        self.window.do_search_win32com(self.params, self.q)


@dataclass
class SearchParams:
    dir_path: str
    search_text: str
    is_strict: bool = False
    match_case: bool = False
    files: Generator = None


@dataclass
class FoundCell:
    path: str
    sheet: str
    cell: object
    cell_value: object = None

    def __init__(self, path, sheet, cell, cell_value):
        self.path = path
        self.sheet = sheet
        self.cell = cell
        self.cell_value = cell_value


class SearchWidget(QWidget, Ui_search_widget):
    singal_log_info = Signal(object)
    singal_log_error = Signal(object)
    single_write_to_table = Signal(object)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.setWindowTitle("searchXlsGui")
        self.setWindowIcon(QIcon(get_icon()))  # 设置图标
        self.bind()

    def bind(self):
        self.btn_open_dir.clicked.connect(self.ui_action_open_dir)
        self.btn_search.clicked.connect(self.ui_action_search)
        # 连接信号到槽函数
        self.singal_log_info.connect(
            lambda *args, **kwargs: self.action_write_to_console(
                "info", *args, **kwargs
            )
        )
        self.singal_log_error.connect(
            lambda *args, **kwargs: self.action_write_to_console(
                "error", *args, **kwargs
            )
        )
        self.single_write_to_table.connect(self.action_write_to_table)
        # 创建右键菜单
        self.table_search_result.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_search_result.customContextMenuRequested.connect(
            self.show_context_menu
        )
        # 初始化参数, 读取store文件
        if os.path.exists(search_xls_store_file):
            try:
                with open(search_xls_store_file, "rb") as f:
                    store = pickle.load(f)
                    self.le_input_dir.setText(store["dir_path"])
                    self.le_input_search_text.setText(store["search_text"])
                    self.le_input_file_filter.setText(store["file_filter"])
                    self.cb_is_strict.setChecked(store["is_strict"])
                    self.cb_is_match_case.setChecked(store["match_case"])
            except Exception as e:
                os.remove(search_xls_store_file)

    def show_context_menu(self, pos):
        # 创建QMenu
        context_menu = QMenu(self)

        # 创建QAction
        open_file_action = QAction("打开文件", self)
        open_folder_action = QAction("打开文件夹", self)  # 新增的打开文件夹的QAction

        # 将QAction添加到QMenu
        context_menu.addAction(open_file_action)
        context_menu.addAction(open_folder_action)

        # 连接QAction的triggered信号到槽函数
        open_file_action.triggered.connect(self.open_file)
        open_folder_action.triggered.connect(self.open_folder)

        # 显示上下文菜单
        context_menu.exec(self.table_search_result.mapToGlobal(pos))

    def open_file(self):
        # 获取选中的行
        selected_row = self.table_search_result.currentRow()
        # 获取选中行的文件路径
        file_path = self.table_search_result.item(selected_row, 0).text()
        # 使用默认的应用程序打开文件
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_folder(self):  # 新增的槽函数
        # 获取选中的行
        selected_row = self.table_search_result.currentRow()
        # 获取选中行的文件路径
        file_path = self.table_search_result.item(selected_row, 0).text()
        # 如果是windows系统
        if sys.platform == "win32":
            # 修改路径为windows格式的路径
            file_path = file_path.replace("/", "\\")
            subprocess.Popen(f'explorer /select,"{file_path}"')
        else:
            # 获取文件所在的文件夹路径
            folder_path = os.path.dirname(file_path)
            # 使用默认的应用程序打开文件夹
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def action_write_to_console(self, type, text):
        if type == "error":
            self.tb_console.append(
                f"<font color='red'>{datetime.now().strftime('%H:%M:%S.%f')[:-3]} : {text}</font> "
            )
        else:
            self.tb_console.append(
                f"<font color='green'>{datetime.now().strftime('%H:%M:%S.%f')[:-3]} </font> : {text}"
            )

    def action_write_to_table(self, found_cell: FoundCell):
        table_widget = self.table_search_result
        # self.emit_log("table_widget.rowCount() = " + str(table_widget.rowCount()))
        if table_widget.rowCount() == 0:
            headers = ("path", "sheet", "cell", "cell_value")
            colum_width_ratio = (4, 1, 1, 1)
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            table_widget.horizontalHeader().setStyleSheet(
                "QHeaderView::section { background-color: lightgrey }"
            )
            table_widget.horizontalHeader().setStretchLastSection(True)
            # 只能选中行,不能选中单元格
            table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

            # colum_width_ratio求和
            for i in range(0, len(headers)):
                table_widget.setColumnWidth(
                    i,
                    1.0
                    * colum_width_ratio[i]
                    / sum(colum_width_ratio)
                    * table_widget.width(),
                )  # Use 'i' instead of '0'
                table_widget.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Interactive
                )

        rowCount = table_widget.rowCount()
        table_widget.setRowCount(rowCount + 1)

        for i, cell_value in enumerate(
            (found_cell.path, found_cell.sheet, found_cell.cell, found_cell.cell_value)
        ):
            item = QTableWidgetItem(str(cell_value))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setToolTip(str(cell_value))
            table_widget.setItem(rowCount, i, item)

    def ui_action_open_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Directory")
        if dir_path:  # 如果用户选择了一个目录
            self.le_input_dir.setText(dir_path)  # 将选中的目录路径设置到文本框中

    def ui_action_search(self):
        dir_path = self.le_input_dir.text()
        if not dir_path:
            self.emit_error("please select a dir")
            return
        search_text = self.le_input_search_text.text()
        file_filter = self.le_input_file_filter.text()
        is_strict = self.cb_is_strict.isChecked()
        match_case = self.cb_is_match_case.isChecked()
        print("filter_filter = " + file_filter)
        files = get_all_files_recursively_xls(dir_path, file_filter)

        params = SearchParams(
            dir_path=dir_path,
            search_text=search_text,
            is_strict=is_strict,
            match_case=match_case,
            files=files,
        )
        # 保存参数到文件
        store = {
            "dir_path": dir_path,
            "search_text": search_text,
            "file_filter": file_filter,
            "is_strict": is_strict,
            "match_case": match_case,
        }
        with open(search_xls_store_file, "wb") as f:
            pickle.dump(store, f)

        # 先终止之前的线程
        old_thread_list = self.thread_list if hasattr(self, "thread_list") else []
        for thread in old_thread_list:
            thread.terminate()

        # 重置table
        self.table_search_result.setRowCount(0)
        self.emit_log("start search")

        # 迭代器转成list
        message_queue = queue.Queue()
        self.file_walk_count = 0
        self.file_count = 0
        self.start_time = datetime.now()
        self.end_time = 0
        for file in params.files:
            message_queue.put(file)
            self.file_count += 1
        # 开启多线程搜索
        thread_list = []
        if self.file_count > 0:
            for i in range(0, 1):
                search_thread = SearchThread(self, params, message_queue)
                search_thread.start()
                thread_list.append(search_thread)
            self.thread_list = thread_list
        # 获取当前 SearchWidget 在 QTabWidget 中的索引
        index = self.parent.search_tab.indexOf(self)
        # 将搜索文本内容设置为当前标签页的名称
        self.parent.search_tab.setTabText(index, search_text)

    # def do_search_xlwings(self, params: SearchParams):
    #     with xw.App(visible=False, add_book=False) as xls_app:
    #         self.emit_log("app start success !")
    #         for file_path in params.files:
    #             self.emit_log(f"searching {file_path}")
    #             workbook = xls_app.books.open(file_path)
    #             # 如果 params.search_text 是空的, 则只查找文件名
    #             if not params.search_text or params.search_text.isspace():
    #                 self.emit_log(f"\t {params.search_text} : {file_path}")
    #                 self.emit_write_to_table(
    #                     FoundCell(path=file_path, sheet="", cell="", cell_value="")
    #                 )
    #                 continue
    #             else:
    #                 for sheet in workbook.sheets:
    #                     first_cell = sheet.api.UsedRange.Find(
    #                         What=params.search_text,
    #                         LookAt=1 if params.is_strict else 2,
    #                         MatchCase=params.match_case,
    #                     )
    #                     if first_cell is not None:
    #                         cell = first_cell
    #                         while True:
    #                             address = cell.GetAddress()
    #                             cell_value = cell.Value
    #                             self.emit_log(
    #                                 f"\t {params.search_text} : {file_path} {sheet.name} - {address}"
    #                             )
    #                             # 写入到FoundCell
    #                             if cell_value_match(
    #                                 cell_value,
    #                                 params.search_text,
    #                                 params.is_strict,
    #                                 params.match_case,
    #                             ):
    #                                 self.emit_write_to_table(
    #                                     FoundCell(
    #                                         path=file_path,
    #                                         sheet=sheet.name,
    #                                         cell=address,
    #                                         cell_value=cell_value,
    #                                     )
    #                                 )
    #                             # found_list.append((sheet.name, address, cell_value))
    #                             cell = sheet.api.UsedRange.FindNext(cell)
    #                             if (
    #                                 not cell
    #                                 or cell.GetAddress() == first_cell.GetAddress()
    #                             ):
    #                                 break
    #             workbook.close()
    #     self.emit_log("")
    #     self.emit_log("")
    #     self.emit_log(" ************************************* ")
    #     self.emit_log(" *          search finished !        * ")
    #     self.emit_log(" ************************************* ")

    def do_search_win32com(self, params: SearchParams, queue: queue.Queue):
        pythoncom.CoInitialize()
        # 启动Excel应用程序
        excel = win32.Dispatch("Excel.Application")
        # 设置Excel为后台运行
        excel.Visible = False
        excel.ScreenUpdating = False
        excel.DisplayAlerts = False
        excel.EnableEvents = False
        excel.Interactive = False
        # 取消excel的警告
        excel.DisplayAlerts = False
        excel.AskToUpdateLinks = False

        while True:
            try:
                file = queue.get_nowait()
            except Exception as e:
                file = None
            if file is None:
                print("-------------------------------- ")
            if file is None and self.end_time == 0:
                self.emit_log(" ************************************* ")
                self.emit_log(" *          search finished !        * ")
                self.emit_log(" ************************************* ")
                self.end_time = datetime.now()
                # 打印cost ms
                self.emit_log(
                    f"cost {(int)((self.end_time - self.start_time).total_seconds() * 1000)} ms"
                )
                break
            self.file_walk_count += 1
            file_walk = self.file_walk_count
            # self.emit_log(f"searching {file}")
            workbook = excel.Workbooks.Open(file)
            # 如果 params.search_text 是空的, 则只查找文件名
            self.emit_log(
                f"\t ({file_walk}/{self.file_count})  search {params.search_text} : {file}"
            )
            if not params.search_text or params.search_text.isspace():
                self.emit_write_to_table(
                    FoundCell(path=file, sheet="", cell="", cell_value="")
                )
                continue
            else:
                for sheet in workbook.Sheets:
                    first_cell = sheet.Cells.Find(
                        What=params.search_text,
                        LookAt=1 if params.is_strict else 2,
                        MatchCase=params.match_case,
                    )
                    if first_cell is not None:
                        cell = first_cell
                        while True:
                            cell_value = cell.Value
                            # 写入到FoundCell
                            if cell_value_match(
                                cell_value,
                                params.search_text,
                                params.is_strict,
                                params.match_case,
                            ):
                                self.emit_write_to_table(
                                    FoundCell(
                                        path=file,
                                        sheet=sheet.Name,
                                        cell=cell.GetAddress(),
                                        cell_value=cell_value,
                                    )
                                )
                            # found_list.append((sheet.name, address, cell_value))
                            cell = sheet.Cells.FindNext(cell)
                            if not cell or cell.GetAddress() == first_cell.GetAddress():
                                break
            workbook.Close()
        # 关闭应用
        excel.Quit()

    def emit_log(self, text):
        print("info: " + text)
        self.singal_log_info.emit(text)

    def emit_error(self, text):
        self.singal_log_error.emit(text)

    def emit_write_to_table(self, found_cell: FoundCell):
        self.single_write_to_table.emit(found_cell)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("searchXlsGui")
        self.setWindowIcon(QIcon(get_icon()))  # 设置图标

        self.search_tab.clear()
        for i in range(1, 2):
            tmp_tab = SearchWidget(self)
            tmp_tab.setObjectName("tab" + str(i))
            self.search_tab.addTab(tmp_tab, "tab" + str(i))
        # tab的最后一个是个button
        button = QPushButton(self)
        self.search_tab.addTab(button, "➕")
        # 当点击的是最后一个是PushButton时, 调用addTab函数
        self.search_tab.tabBarClicked.connect(self.onBarClicked)

        self.xls_app = None
        #
        # self.tab_widget = QTabWidget(self)  # 创建一个QTabWidget实例
        # self.setCentralWidget(self.tab_widget)  # 将QTabWidget设置为主窗口的中心部件

        # self.bind()

    def onBarClicked(self, index):
        widget = self.search_tab.widget(index)
        if isinstance(widget, QPushButton):
            print("QPushButton was clicked.")
            self.addTab()
        else:
            print("Another widget was clicked.")

    def addTab(self):
        # 创建一个新的标签页
        new_tab = SearchWidget(self)
        # 获取标签页的索引
        index = self.search_tab.count() - 1
        # 在标签页中插入新标签页
        self.search_tab.insertTab(index, new_tab, "tab" + str(index + 1))
        # 将新标签页设为当前标签页
        self.search_tab.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
