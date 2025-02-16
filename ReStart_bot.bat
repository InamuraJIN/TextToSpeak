@echo off
taskkill /F /IM python.exe
cd /d "%~dp0"
start python bot.py
exit