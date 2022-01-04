::rd /s /q build
::rd /s /q dist
pyinstaller.exe -i png\csv.ico -y -w -n CsvEditor main.py