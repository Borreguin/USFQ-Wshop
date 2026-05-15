@echo off
REM Añade GLPK a la variable de entorno PATH para la sesión actual
set PATH=C:\glpk-4.65\w64;%PATH%
REM Ejecuta el script principal de Pyomo/TSP
c:/Users/JRG-LAP-80/Documents/GitHub/_Soluciones/Grupo1/.venv/Scripts/python.exe TSP.py
pause
