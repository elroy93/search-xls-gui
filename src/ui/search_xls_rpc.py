from abc import ABCMeta
from abc import abstractmethod


class SearchXlsServerRpcService(metaclass=ABCMeta):
    @abstractmethod
    def to_server_error(self, text):
        pass

    @abstractmethod
    def to_server_log(self, text):
        pass

    @abstractmethod
    def to_server_report_finsh_one_file(self, file):
        pass

    @abstractmethod
    def to_server_report_search_result(self, found_cell):
        pass

    @abstractmethod
    def to_server_poll_file(self):
        pass

    @abstractmethod
    def to_server_report_search_finished(self, process_id):
        pass

    # @abstractmethod
    # def to_server_test_connection(self, text):
    #     pass
