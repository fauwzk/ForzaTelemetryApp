@echo off
rmdir /s /q output
pyinstaller --noconfirm --onefile --console --name "ForzaTelemetryApp" --add-data "data_format.txt;." --add-data "data_gen.py;."  "main.py"
ren dist output
rmdir /s /q build
