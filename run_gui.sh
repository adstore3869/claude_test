#!/bin/bash
# Linux/Mac용 GUI 실행 스크립트

echo "==============================================="
echo "Video Person Tracker - GUI 실행"
echo "==============================================="
echo ""

python3 run_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "오류가 발생했습니다."
    read -p "Press Enter to continue..."
fi
