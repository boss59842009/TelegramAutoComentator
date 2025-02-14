@echo off
chcp 65001 > nul

pip show telethon > nul || pip install telethon

echo Запускаю скрипт...
timeout /t 3 > nul


python main.py
pause