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

echo Setup complete.

del search_xls_gui.exe
::删除上级目录下的 search_xls_gui.exe 文件
del ..\search_xls_gui.exe

:: 使用页面
:: auto-py-to-exe

pyinstaller --noconfirm --onefile --console --icon "./resource/search.ico" --distpath "." "./src/search_xls_gui.py" --noconsole

:: 删除当前文件夹下的 search_xls_gui.spec 文件
del search_xls_gui.spec
:: 当前文件夹下的 search_xls_gui.exe copy到上一级目录
copy search_xls_gui.exe ..

:: 退出当前的虚拟环境

echo Deactivating virtual environment...
deactivate

pause
