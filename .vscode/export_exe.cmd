@echo off
rmdir /s /q dist
python -m black src\*.py
pyinstaller --noconfirm --onefile --console --name "ForzaTelemetryApp" --add-data "src\data_format.txt;." --add-data "src\font.otf;." --add-data "src\data_gen.py;." --add-data "src\default.ini;." "src\main.py"
rmdir /s /q build
