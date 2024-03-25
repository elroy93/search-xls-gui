import os
import pickle
import random
import signal
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from multiprocessing import Process

import zerorpc
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
)
from PySide6.QtWidgets import QMenu

from src.model import SearchParams, FoundCell
from src.search_worker_client import SearchClientWorker
from src.search_worker_server import SearchServerWorker
from src.ui.ui_main import Ui_MainWindow
from src.ui.ui_search_widget import Ui_search_widget
from src.utils import get_all_files_recursively_xls, get_icon, find_free_port

search_xls_store_file = ".search_xls_gui_store.pkl"

def search_in_process(port, process_id, params: SearchParams, part_files):
    """
    在一个进程中搜索, 这里是在单独的进程中执行的
    :param port:                进行通信的端口号
    :param process_id:          一次搜索会开启多个进程,每个进程有一个id
    """
    # print("------------------- run search in process -------------------", process_id, params, part_files)
    worker = SearchClientWorker(port, process_id)
    worker.do_search_openpyxl(params, part_files)
    worker.stop()

class SearchWidget(QWidget, Ui_search_widget):
    singal_log_info = Signal(object)
    singal_log_error = Signal(object)
    single_write_to_table = Signal(object)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.setWindowTitle("search_xls_gui.exe")
        self.setWindowIcon(QIcon(get_icon()))  # 设置图标

        # 异步的初始化一个rpc server
        self.port = find_free_port()
        # 从 4242 开始找一个可用的端
        self.serverStarter = SearchWorkerStarter(self, self.port)
        self.thread = threading.Thread(target=self.serverStarter.run)
        self.thread.start()
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
        file_path = self.table_search_result.item(selected_row, 0).toolTip()
        # 使用默认的应用程序打开文件
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_folder(self):  # 新增的槽函数
        # 获取选中的行
        selected_row = self.table_search_result.currentRow()
        # 获取选中行的文件路径
        file_path = self.table_search_result.item(selected_row, 0).toolTip()
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
            headers = ("path", "sheet", "cell", "cell_value", "row")
            colum_width_ratio = (15, 10, 8, 20, 40)
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            table_widget.horizontalHeader().setStyleSheet(
                "QHeaderView::section { background-color: rgb(242, 242, 242) }"
            )
            # 自定义工具提示样式
            tooltip_style = """
            QToolTip {
                background-color: yellow;
                color: black;
                border: 1px solid black;
            }
            QTableWidget::item:hover {
                background-color: lightblue;
            }
            """
            table_widget.setStyleSheet(tooltip_style)
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
                (found_cell.path, found_cell.sheet, found_cell.cell, found_cell.cell_value, found_cell.row_all)
        ):
            if i == 0:
                file_name = os.path.basename(cell_value)
                item = QTableWidgetItem(file_name)
            else:
                item = QTableWidgetItem(str(cell_value))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setToolTip(str(cell_value))
            table_widget.setItem(rowCount, i, item)

    def ui_action_open_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Directory")
        if dir_path:  # 如果用户选择了一个目录
            self.le_input_dir.setText(dir_path)  # 将选中的目录路径设置到文本框中

    def ui_stop_to_search(self):
        # 停止的时候
        self.btn_search.setStyleSheet("background-color: rgb(230, 230, 230)")
        self.btn_search.setText("搜索")
        self.emit_log("stop search")
        self.serverStarter.search_worker.files.clear()

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
        file_generator = get_all_files_recursively_xls(dir_path, file_filter)

        params = SearchParams(
            dir_path=dir_path,
            search_text=search_text,
            is_strict=is_strict,
            match_case=match_case,
        )
        # 保存参数到文件
        store = {
            "dir_path": dir_path,
            "search_text": search_text,
            "file_filter": file_filter,
            "is_strict": is_strict,
            "match_case": match_case,
        }
        try:
            with open(search_xls_store_file, "wb") as f:
                pickle.dump(store, f)
        except Exception as e:
            pass
        # 先终止之前的线程
        old_thread_list = self.thread_list if hasattr(self, "thread_list") else []
        for thread in old_thread_list:
            thread.terminate()

        mode = self.btn_search.text()
        if "停止" in mode:
            self.ui_stop_to_search()
        else:
            self.btn_search.setStyleSheet("background-color: red")
            self.btn_search.setText("停止")
            # 获取当前 SearchWidget 在 QTabWidget 中的索引
            index = self.parent.search_tab.indexOf(self)
            # 将搜索文本内容设置为当前标签页的名称
            self.parent.search_tab.setTabText(index, f"{file_filter}:{search_text}")

            # 重置table
            self.table_search_result.setRowCount(0)
            self.emit_log("start search")
            try:
                with open(search_xls_store_file, "wb") as f:
                    pickle.dump(store, f)
            except Exception as e:
                pass
            # 先终止之前的线程
            old_thread_list = self.thread_list if hasattr(self, "thread_list") else []
            for thread in old_thread_list:
                thread.terminate()
            # 迭代器转成list
            self.file_walk_count = 0
            self.file_count = 0
            self.start_time = datetime.now()
            self.end_time = 0
            files = []
            for file in file_generator:
                files.append(file)
                self.file_count += 1

            # files 打散
            # 按照文件大小进行排序, 先搜索小的文件
            files.sort(key=lambda x: os.path.getsize(x))
            # random.shuffle(files)
            # 设置为cpu*2
            thread_num = os.cpu_count()

            self.serverStarter.search_file_count.clear()
            self.serverStarter.search_file_count.append(self.file_count)
            self.serverStarter.search_worker.reset()
            self.serverStarter.search_worker.set_thread_num(thread_num)
            self.serverStarter.search_worker.files.clear()
            self.serverStarter.search_worker.files.extend(files)
            # 开启多进程搜索
            self.emit_log("--- 开始搜索 --- ")
            if self.file_count > 0:
                for i in range(thread_num):
                    # print("start = " + str(start) + ", end = " + str(end))
                    # 开启第一个进程
                    thread = Process(
                        target=search_in_process,
                        args=(
                            self.port,
                            i,
                            params,
                            []
                        ),
                    )
                    thread.start()
            else:
                self.emit_log("没有匹配的文件")
                self.ui_stop_to_search()
            self.emit_log("--- 进程开启结束 --- ")

    def emit_log(self, text):
        print("info: " + text)
        self.singal_log_info.emit(text)

    def emit_error(self, text):
        self.singal_log_error.emit(text)

    def emit_write_to_table(self, found_cell: FoundCell):
        self.single_write_to_table.emit(found_cell)


class SearchWorkerStarter(object):
    def __init__(self, search_widget, port):
        self.search_widget = search_widget
        self.port = port
        self.search_file_count = []
        self.search_worker = SearchServerWorker(self.search_widget, self.search_file_count)
        self.search_widget.emit_log("start rpc server port : " + str(port))
        self.rpc_uuid = uuid.uuid1()

    def run(self):
        self.server = zerorpc.Server(self.search_worker)
        self.server.bind("tcp://127.0.0.1:" + str(self.port))
        self.server.run()

    def rpc_server_stop(self):
        try:
            self.server.close()
        except Exception as e:
            pass

    def get_uuid(self):
        return self.rpc_uuid


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("search_xls_gui.exe")
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
        # 调整tab的样式
        self.search_tab.setStyleSheet(
            """
            QTabBar::tab {
                background: rgb(230, 230, 230);
                border: 1px solid lightgray;
                padding: 3px;
                min-width: 70px;
            }
            QTabBar::tab:selected {
                background: white ;
                margin-bottom: -1px;
            }
            """
        )
        self.xls_app = None
        # 设置标签页可以关闭，并连接tabCloseRequested信号到removeTab槽函数
        self.search_tab.setTabsClosable(True)
        self.search_tab.tabCloseRequested.connect(self.removeTab)

    def closeEvent(self, event):
        # Perform your action here
        print("MainWindow is being closed")
        # Call the parent class's closeEvent method to do the actual closing
        super().closeEvent(event)
        # 关闭当前进程及子进程
        os.kill(os.getpid(), signal.SIGTERM)

    def removeTab(self, index):
        widget = self.search_tab.widget(index)
        if isinstance(widget, QPushButton):
            pass
        else:
            search_widget = self.search_tab.widget(index)
            search_widget.serverStarter.rpc_server_stop()
            self.search_tab.removeTab(index)

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
    import multiprocessing

    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
