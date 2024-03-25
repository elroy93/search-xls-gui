from datetime import datetime

from src.model import FoundCell
from src.ui.search_xls_rpc import SearchXlsServerRpcService


class SearchServerWorker(SearchXlsServerRpcService):
    def __init__(self, search_widget, search_file_count_arr):
        self.search_widget = search_widget
        self.search_file_count_arr = search_file_count_arr
        self.has_search_file_count = 0
        self.files = []
        self.search_thread_num = 0

    def to_server_error(self, text):
        self.search_widget.emit_error(text)

    def to_server_log(self, text):
        self.search_widget.emit_log(text)

    def to_server_report_finsh_one_file(self, file):
        self.has_search_file_count = self.has_search_file_count + 1
        self.search_widget.emit_log(f"finish {self.has_search_file_count}/{self.search_file_count_arr[0]} : {file}")

    def to_server_poll_file(self):
        if len(self.files) > 0:
            return self.files.pop()
        else:
            return None

    def to_server_report_search_finished(self, process_id):
        # self.search_widget.emit_error("process_id = " + str(process_id) + " finished")
        self.has_search_finished_process_count = self.has_search_finished_process_count + 1
        if self.has_search_finished_process_count == self.search_thread_num:
            self.search_widget.ui_stop_to_search()
            cost_time = datetime.now() - self.start_time
            # 打印时间,只保留到秒
            cost_time = str(cost_time).split(".")[0]
            self.search_widget.emit_log("search finished")
            self.search_widget.emit_log(f"***********************")
            self.search_widget.emit_log(f"耗时 : {cost_time}")
            self.search_widget.emit_log(f"***********************")

    def to_server_report_search_result(self, found_cell_dict):
        # print("rpc_write_to_table, found_cell = " + str(found_cell_dict))
        # dict 转成 FoundCell
        found_cell = FoundCell(
            path=found_cell_dict["path"],
            sheet=found_cell_dict["sheet"],
            cell=found_cell_dict["cell"],
            cell_value=found_cell_dict["cell_value"],
            row_all=found_cell_dict["row_all"],
        )
        self.search_widget.emit_write_to_table(found_cell)

    def test_rpc(self, name):
        print("+++++++++++++++ test_rpc, name = " + name)

    def reset(self):
        self.start_time = datetime.now()
        self.has_search_finished_process_count = 0
        self.has_search_file_count = 0
        self.files = []
        self.search_thread_num = 0

    def set_thread_num(self, thread_num):
        self.search_thread_num = thread_num
