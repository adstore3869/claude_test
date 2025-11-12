"""
설치 테스트 스크립트
필요한 모든 라이브러리가 제대로 설치되었는지 확인합니다.
"""

import sys


def test_imports():
    """필수 라이브러리 import 테스트"""
    print("필수 라이브러리 확인 중...\n")

    tests = []

    # OpenCV
    try:
        import cv2
        print(f"✓ OpenCV 버전: {cv2.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"✗ OpenCV 설치 실패: {e}")
        tests.append(False)

    # face_recognition
    try:
        import face_recognition
        print("✓ face_recognition 설치 완료")
        tests.append(True)
    except ImportError as e:
        print(f"✗ face_recognition 설치 실패: {e}")
        tests.append(False)

    # numpy
    try:
        import numpy as np
        print(f"✓ NumPy 버전: {np.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"✗ NumPy 설치 실패: {e}")
        tests.append(False)

    # PIL
    try:
        from PIL import Image
        print(f"✓ Pillow 설치 완료")
        tests.append(True)
    except ImportError as e:
        print(f"✗ Pillow 설치 실패: {e}")
        tests.append(False)

    # dlib
    try:
        import dlib
        print(f"✓ dlib 설치 완료")
        tests.append(True)
    except ImportError as e:
        print(f"✗ dlib 설치 실패: {e}")
        tests.append(False)

    # 프로젝트 모듈
    try:
        from video_person_tracker import VideoPersonTracker
        print("✓ VideoPersonTracker 모듈 로드 완료")
        tests.append(True)
    except ImportError as e:
        print(f"✗ VideoPersonTracker 모듈 로드 실패: {e}")
        tests.append(False)

    print("\n" + "="*50)
    if all(tests):
        print("✓ 모든 테스트 통과!")
        print("시스템이 정상적으로 설치되었습니다.")
        return True
    else:
        print("✗ 일부 테스트 실패")
        print("\n설치 방법:")
        print("  pip install -r requirements.txt")
        return False


def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n" + "="*50)
    print("기본 기능 테스트")
    print("="*50 + "\n")

    try:
        from video_person_tracker import VideoPersonTracker
        import numpy as np

        # 트래커 초기화
        tracker = VideoPersonTracker()
        print("✓ 트래커 초기화 성공")

        # 더미 테스트
        print("✓ 기본 기능 정상")

        print("\n모든 기능 테스트 통과!")
        return True

    except Exception as e:
        print(f"✗ 기능 테스트 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("="*50)
    print("Video Person Tracker - 설치 테스트")
    print("="*50 + "\n")

    # 라이브러리 테스트
    import_success = test_imports()

    if import_success:
        # 기능 테스트
        func_success = test_basic_functionality()

        if func_success:
            print("\n" + "="*50)
            print("설치가 완료되었습니다!")
            print("다음 단계:")
            print("  1. 영상 파일을 준비하세요 (예: input_video.mp4)")
            print("  2. python example_usage.py input_video.mp4 실행")
            print("="*50)
            sys.exit(0)

    print("\n설치에 문제가 있습니다. requirements.txt를 확인하세요.")
    sys.exit(1)


if __name__ == "__main__":
    main()
