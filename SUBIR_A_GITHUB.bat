@echo off
title Subir Firma a GitHub
color 0B
echo ========================================================
echo        SUBIENDO FIRMA A GITHUB (EddSL2/Firma)
echo ========================================================
echo.
cd /d "c:\Users\eddus\OneDrive\Desktop\FirmaGmail"

echo Comprobando estado de git...
git status
echo.
echo Ejecutando git push origin main...
git push -u origin main

echo.
echo ========================================================
if %ERRORLEVEL% EQU 0 (
    echo   [EXITO] Repositorio subido correctamente a GitHub!
) else (
    echo   [AVISO] Hubo un problema al subir. Revisa el mensaje arriba.
)
echo ========================================================
echo.
pause
