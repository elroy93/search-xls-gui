@echo off
chcp 65001

echo Creating virtual environment...

python -m venv env
echo Activating virtual environment...
call env\Scripts\activate

:: 打印当前目录
echo %cd%

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

python search_xls_gui.py
