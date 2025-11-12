"""
Video Person Tracker - 사용 예제
"""

from video_person_tracker import VideoPersonTracker
import sys


def example_basic():
    """기본 사용 예제"""
    print("="*60)
    print("기본 사용 예제")
    print("="*60)

    # 트래커 초기화
    tracker = VideoPersonTracker()

    # 영상 처리
    video_path = "input_video.mp4"
    print(f"\n영상 처리 시작: {video_path}")

    try:
        results = tracker.process_video(video_path)

        # 결과 저장
        tracker.save_results("results.json")

        # 결과 출력
        tracker.print_summary()

    except FileNotFoundError as e:
        print(f"오류: {e}")
        print("사용법: input_video.mp4 파일을 현재 디렉토리에 배치하세요.")


def example_advanced():
    """고급 사용 예제 - 성능 최적화 및 결과 영상 생성"""
    print("="*60)
    print("고급 사용 예제")
    print("="*60)

    # 설정 옵션
    # - frame_skip=5: 5프레임마다 분석 (처리 속도 5배 향상)
    # - tolerance=0.6: 얼굴 인식 정확도 (기본값)
    # - output_video=True: 결과 영상 생성
    tracker = VideoPersonTracker(
        frame_skip=5,
        tolerance=0.6,
        output_video=True
    )

    video_path = "input_video.mp4"
    output_path = "output_video.mp4"

    print(f"\n영상 처리 시작: {video_path}")
    print(f"결과 영상 저장 위치: {output_path}")

    try:
        results = tracker.process_video(video_path, output_path=output_path)

        # 결과 저장
        tracker.save_results("results_advanced.json")

        # 결과 출력
        tracker.print_summary()

        # 개별 인물 정보 조회
        print("\n개별 인물 정보:")
        for i in range(tracker.next_person_id):
            person_info = tracker.get_person_summary(i)
            if person_info:
                print(f"\nPerson {i} 상세 정보:")
                print(f"  총 출연 프레임: {len(person_info['frames'])}개")
                print(f"  첫 5개 출연 프레임: {person_info['frames'][:5]}")

    except FileNotFoundError as e:
        print(f"오류: {e}")
        print("사용법: input_video.mp4 파일을 현재 디렉토리에 배치하세요.")


def example_custom():
    """커스텀 설정 예제"""
    print("="*60)
    print("커스텀 설정 예제")
    print("="*60)

    # 매우 높은 정확도 설정 (느리지만 정확)
    tracker_strict = VideoPersonTracker(
        frame_skip=1,  # 모든 프레임 분석
        tolerance=0.5,  # 엄격한 매칭
        output_video=False
    )

    # 빠른 처리 설정 (빠르지만 일부 프레임 스킵)
    tracker_fast = VideoPersonTracker(
        frame_skip=10,  # 10프레임마다 분석
        tolerance=0.65,  # 조금 느슨한 매칭
        output_video=False
    )

    print("\n설정 완료. 필요에 따라 tracker_strict 또는 tracker_fast를 사용하세요.")


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("Video Person Tracker - 영상 인물 추적 시스템")
    print("="*60 + "\n")

    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        output_json = sys.argv[2] if len(sys.argv) > 2 else "results.json"

        print(f"입력 영상: {video_path}")
        print(f"결과 저장: {output_json}\n")

        # 트래커 실행
        tracker = VideoPersonTracker(frame_skip=3)

        try:
            tracker.process_video(video_path)
            tracker.save_results(output_json)
            tracker.print_summary()

        except Exception as e:
            print(f"오류 발생: {e}")
            sys.exit(1)

    else:
        print("사용법:")
        print("  python example_usage.py <video_path> [output_json]")
        print("\n예제:")
        print("  python example_usage.py input_video.mp4")
        print("  python example_usage.py input_video.mp4 my_results.json")
        print("\n또는 코드를 수정하여 example_basic() 또는 example_advanced() 함수를 호출하세요.")


if __name__ == "__main__":
    main()
