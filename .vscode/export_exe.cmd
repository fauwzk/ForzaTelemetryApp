@echo off
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q output
python -m black src\*.py
pyinstaller --noconfirm --onefile --console --name "ForzaTelemetryApp" --add-data "src\data_format.txt;." --add-data "src\font.otf;." --add-data "src\data_gen.py;." --add-data "src\default.ini;." "src\main.py"
ren dist output
rmdir /s /q build
