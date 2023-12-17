import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Generator

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView

from src.ui.ui_main import Ui_MainWindow  # 确保这个导入路径是正确的
from src.utils import get_all_files_recursively_xls


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


class MainWindow(QMainWindow, Ui_MainWindow):
    singal_log_info = Signal(object)  # 定义一个新的信号，这个信号会发送一个字符串
    singal_log_error = Signal(object)  # 定义一个新的信号，这个信号会发送一个字符串

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.bind()

    def bind(self):
        self.btn_open_dir.clicked.connect(self.ui_action_open_dir)
        self.btn_search.clicked.connect(self.ui_action_search)
        # 连接信号到槽函数
        self.singal_log_info.connect(lambda *args, **kwargs: self.action_write_to_console("info", *args, **kwargs))
        self.singal_log_error.connect(lambda *args, **kwargs: self.action_write_to_console("error", *args, **kwargs))

    def action_write_to_console(self, type, text):
        if type == "error":
            self.tb_console.append(f"<font color='red'>{datetime.now().strftime('%H:%M:%S.%f')[:-3]} : {text}</font> ")
        else:
            self.tb_console.append(
                f"<font color='green'>{datetime.now().strftime('%H:%M:%S.%f')[:-3]} </font> : {text}")

    def ui_action_open_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Directory")
        if dir_path:  # 如果用户选择了一个目录
            self.le_input_dir.setText(dir_path)  # 将选中的目录路径设置到文本框中

    def ui_action_search(self):
        dir_path = self.le_input_dir.text()
        if not dir_path:
            self.error("please select a dir")
            return
        search_text = self.le_input_search_text.text()
        files = get_all_files_recursively_xls(dir_path)
        params = SearchParams(dir_path=dir_path,
                              search_text=search_text,
                              is_strict=False,
                              match_case=False,
                              files=files)
        # 可以开一个线程来执行搜索
        self.do_search(params)

    def ui_write_to_table(self, found_cell: FoundCell):
        table_widget = self.table_search_result

        self.info("table_widget.rowCount() = " + str(table_widget.rowCount()))
        if table_widget.rowCount() == 0:
            headers = ("path", "sheet", "cell", "cell_value")
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            table_widget.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: lightgrey }")
            # 使每列宽度自动调整以填充表格宽度
            header = table_widget.horizontalHeader()
            # 为大部分列设置ResizeToContents模式
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for i in range(1, table_widget.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                header.setMinimumSectionSize(120)

        rowCount = table_widget.rowCount()
        table_widget.setRowCount(rowCount + 1)

        for i, cell_value in enumerate((found_cell.path, found_cell.sheet, found_cell.cell, found_cell.cell_value)):
            item = QTableWidgetItem(str(cell_value))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item.setToolTip(str(cell_value))
            table_widget.setItem(rowCount, i, item)


    def do_search(self, params: SearchParams):
        for file in params.files:
            self.info(f"searching {file}")
            pass
        self.ui_write_to_table(
            FoundCell(path="测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试",
                      sheet="测试测试测试", cell="测试", cell_value="测试"))

    def info(self, text):
        self.singal_log_info.emit(text)

    def error(self, text):
        self.singal_log_error.emit(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
