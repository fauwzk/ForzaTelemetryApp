@echo off
rmdir /s /q dist
rmdir /s /q output
pyinstaller --noconfirm --onefile --console --name "ForzaTelemetryApp" --add-data "data_format.txt;." --add-data "font.ttf;." --add-data "data_gen.py;." --add-data "fta.ini;." "main.py"
ren dist output
rmdir /s /q build
