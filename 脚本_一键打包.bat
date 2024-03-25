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

echo venv setup completed.

:: pyinstaller --noconfirm --onefile --console --icon "./resource/search.ico" --distpath "." "./src/search_xls_gui.py" --noconsole
pyinstaller search_xls_gui.spec

:: 在资源管理器中当前目录下的dist文件夹
explorer.exe dist

echo Press any key to continue...

deactivate
pause
