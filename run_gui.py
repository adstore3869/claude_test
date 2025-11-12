#!/usr/bin/env python3
"""
Video Person Tracker GUI 실행 스크립트
간단하게 GUI 애플리케이션을 실행합니다.
"""

import sys
import os

def check_dependencies():
    """필수 라이브러리 확인"""
    missing = []

    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")

    try:
        import face_recognition
    except ImportError:
        missing.append("face-recognition")

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import PIL
    except ImportError:
        missing.append("pillow")

    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")

    if missing:
        print("오류: 다음 라이브러리가 설치되지 않았습니다:")
        for lib in missing:
            print(f"  - {lib}")
        print("\n설치 방법:")
        print("  pip install -r requirements.txt")
        return False

    return True


def main():
    """메인 함수"""
    print("="*60)
    print("Video Person Tracker - GUI 실행")
    print("="*60)
    print()

    # 의존성 확인
    print("라이브러리 확인 중...")
    if not check_dependencies():
        sys.exit(1)

    print("✓ 모든 라이브러리가 설치되어 있습니다.\n")

    # GUI 실행
    print("GUI 애플리케이션을 시작합니다...")
    print("창이 나타나지 않으면 태스크바를 확인하세요.\n")

    try:
        from gui_app import main as gui_main
        gui_main()
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
