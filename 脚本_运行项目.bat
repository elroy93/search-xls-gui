@echo off
chcp 65001

if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin


echo 创建虚拟环境...

IF EXIST env (
    echo 虚拟环境已存在，跳过创建步骤。
) ELSE (
    python -m venv env
    IF ERRORLEVEL 1 (
        echo 创建虚拟环境失败，退出。
        exit /b 1
    )
)

echo 激活虚拟环境...
call env\Scripts\activate
IF ERRORLEVEL 1 (
    echo 激活虚拟环境失败，退出。
    exit /b 1
)

:: 打印当前目录
echo %cd%

echo 从requirements.txt安装依赖...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo 安装依赖失败，退出。
    exit /b 1
)

echo 脚本执行完成。
python search_xls_gui.py
pause
