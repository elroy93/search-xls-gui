
import os

# 递归获取目录下的所有文件, 返回一个生成器
def get_all_files_recursively_xls(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            # ~$
            if file.startswith("~$"):
                continue
            if file.endswith(".xlsx") or file.endswith(".xls"):
                yield os.path.join(root, file)