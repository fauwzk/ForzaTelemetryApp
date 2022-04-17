@echo off
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q output
python -m black *.py
pyinstaller --noconfirm --onefile --console --name "ForzaTelemetryApp" --add-data "data_format.txt;." --add-data "font.otf;." --add-data "data_gen.py;." --add-data "fta.ini;." "main.py"
ren dist output
rmdir /s /q build
