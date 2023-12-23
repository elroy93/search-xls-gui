import os


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
    return file_path.endswith(".xlsx") or file_path.endswith(".xls")


def file_match_filters(file_path, file_filters):
    # file_filters是多规则, 使用空格分隔,满足所有的规则才返回true
    if not file_filters:
        return True
    for file_filter in file_filters.split(" "):
        if not file_match_filter(file_path, file_filter):
            return False
    return True


def file_match_filter(file_path, file_filter):
    # 如果是空的或者是空格, 返回true
    if not file_filter or file_filter.isspace():
        return True
    # 如果filter_filter是!开头, 如果文件包含匹配的字符串, 返回false
    if file_filter.startswith("!"):
        return file_filter[1:] not in file_path
    # 否则, 必须包含匹配的字符串, 返回true
    return file_filter in file_path


def cell_value_match(cell_value, search_text, is_strict, match_case):
    cell_value = str(cell_value)
    search_text = str(search_text)
    if not search_text or search_text.isspace():
        return True
    if is_strict:
        # 这里需要处理一下前后空格, 以及小数点后面的0
        return search_text.strip() == cell_value.strip().rstrip("0").rstrip(".")
    else:
        if match_case:
            return search_text.lower() in cell_value.lower()
        else:
            return search_text in cell_value
