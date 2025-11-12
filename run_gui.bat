@echo off
REM Windows용 GUI 실행 배치 파일

echo ===============================================
echo Video Person Tracker - GUI 실행
echo ===============================================
echo.

python run_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 오류가 발생했습니다.
    pause
)
