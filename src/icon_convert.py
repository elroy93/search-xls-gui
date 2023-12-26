import base64


# icon图标转换为py文件
if __name__ == "__main__":
    with open("../resource/search.ico", "rb") as icon:
        icon_str = base64.b64encode(icon.read())
        icon_bytes = "icon_bytes = " + str(icon_str)
    with open("icon_search.py", "w+") as icon_py:
        icon_py.write(icon_bytes)
