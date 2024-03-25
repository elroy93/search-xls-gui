import base64
import os

from PySide6.QtGui import QPixmap

from src.icon_search import icon_bytes


# 递归获取目录下的所有文件, 返回一个生成器
def get_all_files_recursively_xls(path, file_filter):
    for root, dirs, files in os.walk(path):
        for file in files:
            # ~$
            if file.startswith("~$"):
                continue
            if file_ext_is_xls(file) and file_match_filters(file, file_filter):
                yield os.path.join(root, file)


def file_ext_is_xls(file_path):
    return (
        file_path.endswith(".xlsx")
        or file_path.endswith(".xls")
        or file_path.endswith(".xlsm")
    )


def file_match_filters(file_path, file_filters):
    # file_filters是多规则, 使用空格分隔,满足所有的规则才返回true
    if not file_filters:
        return True
    match_any = False
    texts = file_filters.split(" ")
    for file_filter in texts :
        if not file_filter.startswith("!") :
            match_any = match_any or file_match_filter(file_path, file_filter)
        else :
            # 如果filter_filter是!开头, 如果文件包含匹配的字符串, 返回false
            if file_filter[1:] in file_path :
                return False
    return match_any

def file_match_filter(file_path, file_filter):
    # 如果是空的或者是空格, 返回true
    if not file_filter or file_filter.isspace():
        return True
    # 否则, 必须包含匹配的字符串, 返回true
    return file_filter in file_path


def cell_value_match(cell_value, search_text, is_strict, match_case):
    cell_value = str(cell_value).strip()
    search_text = str(search_text).strip()
    if not search_text or search_text.isspace():
        return True
    if is_strict:
        # print("is_strict  cell_value = " + cell_value + ", search_text = " + search_text)
        # 这里需要处理一下前后空格, 以及小数点和小数点后面的0
        # 如果cell_value是个数字
        return search_text == cell_value
        # if cell_value.isdigit() and search_text.isdigit():
        #     return abs(float(search_text) - float(cell_value)) < 0.0001
        # else:
        #     return search_text == cell_value
    else:
        if match_case:
            return search_text in cell_value
        else:
            return search_text.lower() in cell_value.lower()


# 图标bytes转成pixmap格式
def get_icon():
    icon_img = base64.b64decode(icon_bytes)  # 解码
    icon_pixmap = QPixmap()  # 新建QPixmap对象
    icon_pixmap.loadFromData(icon_img)  # 往QPixmap中写入数据
    return icon_pixmap


import socket


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        # 立即释放端口
        s.close()
    return port
