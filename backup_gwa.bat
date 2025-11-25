@echo off
REM -----------------------------------------------------------
REM SCRIPT DE RESPALDO PARA GLOBAL WIRED AGENCY
REM Crea una carpeta de backup con fecha y hora.
REM -----------------------------------------------------------

REM --- Variables de fecha y hora para el nombre del backup ---
REM Formato: YYYYMMDD_HHMMSS
set YYYY=%date:~-4%
set MM=%date:~4,2%
set DD=%date:~7,2%
set HH=%time:~0,2%
set MI=%time:~3,2%
set SS=%time:~6,2%

REM Limpiar espacios en blanco en la hora (crucial para Windows)
set HH=%HH: =0%

set "BACKUP_DIR=backup_GWA_%YYYY%%MM%%DD%_%HH%%MI%%SS%"

echo.
echo Creando carpeta de respaldo: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"

echo Copiando archivos esenciales de la arquitectura...
REM /E: Copia directorios y subdirectorios, incluyendo los vacíos
REM /I: Asume que el destino es un directorio si no existe
REM /Y: Suprime el aviso para sobrescribir archivos

xcopy /E /I /Y "app_frontend.py" "%BACKUP_DIR%\"
xcopy /E /I /Y "logo.png" "%BACKUP_DIR%\"
xcopy /E /I /Y "gwa_studio_core" "%BACKUP_DIR%\gwa_studio_core\"
xcopy /E /I /Y "gwa_studio_llms" "%BACKUP_DIR%\gwa_studio_llms\"
xcopy /E /I /Y "requirements.txt" "%BACKUP_DIR%\"

echo.
echo Respaldo COMPLETO en la carpeta: %BACKUP_DIR%
echo.
pause