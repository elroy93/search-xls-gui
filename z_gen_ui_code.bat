
:: 将当前目录下的所有的.ui文件使用uic转换成.py文件

@echo off
chcp 65001

echo Creating virtual environment...

python -m venv venv
echo Activating virtual environment...
call env\Scripts\activate

:: 打印当前目录
echo %cd%

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Setup complete.

cd src\ui

for /r %%i in (*.ui) do (
    echo %%i
    ::python -m pyside6-uic %%i -o ui_%%~ni.py
    pyside6-uic %%i -o ui_%%~ni.py
)
