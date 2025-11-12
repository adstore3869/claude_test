#!/usr/bin/env python3
"""
Video Person Tracker - CLI 인터페이스
명령줄에서 간편하게 영상을 처리할 수 있습니다.
"""

import argparse
import sys
import os
from video_person_tracker import VideoPersonTracker


def main():
    parser = argparse.ArgumentParser(
        description='영상에서 인물을 추적하고 출연 횟수를 기록합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  # 기본 사용
  python cli.py -i input.mp4

  # 결과 파일 지정
  python cli.py -i input.mp4 -o results.json

  # 결과 영상 생성
  python cli.py -i input.mp4 --output-video output.mp4

  # 성능 최적화 (5프레임마다 분석)
  python cli.py -i input.mp4 --frame-skip 5

  # 정확도 조정
  python cli.py -i input.mp4 --tolerance 0.5

  # 모든 옵션 사용
  python cli.py -i input.mp4 -o results.json --output-video output.mp4 --frame-skip 3 --tolerance 0.6
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='입력 영상 파일 경로 (필수)'
    )

    parser.add_argument(
        '-o', '--output',
        default='results.json',
        help='결과 JSON 파일 경로 (기본값: results.json)'
    )

    parser.add_argument(
        '--output-video',
        help='결과 영상 파일 경로 (지정 시 처리된 영상 생성)'
    )

    parser.add_argument(
        '--frame-skip',
        type=int,
        default=1,
        help='프레임 스킵 간격 (1=모든 프레임, 5=5프레임마다, 기본값: 1)'
    )

    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.6,
        help='얼굴 인식 정확도 (0.0-1.0, 낮을수록 엄격, 기본값: 0.6)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='진행 상황 출력 최소화'
    )

    args = parser.parse_args()

    # 입력 파일 확인
    if not os.path.exists(args.input):
        print(f"오류: 입력 파일을 찾을 수 없습니다: {args.input}")
        sys.exit(1)

    # 설정 출력
    if not args.quiet:
        print("="*60)
        print("Video Person Tracker")
        print("="*60)
        print(f"입력 영상: {args.input}")
        print(f"결과 파일: {args.output}")
        if args.output_video:
            print(f"출력 영상: {args.output_video}")
        print(f"프레임 스킵: {args.frame_skip}")
        print(f"정확도 임계값: {args.tolerance}")
        print("="*60 + "\n")

    try:
        # 트래커 초기화
        tracker = VideoPersonTracker(
            frame_skip=args.frame_skip,
            tolerance=args.tolerance,
            output_video=args.output_video is not None
        )

        # 영상 처리
        if not args.quiet:
            print("영상 처리 시작...\n")

        tracker.process_video(args.input, output_path=args.output_video)

        # 결과 저장
        tracker.save_results(args.output)

        # 요약 출력
        if not args.quiet:
            tracker.print_summary()

            print(f"\n처리 완료!")
            print(f"결과가 '{args.output}'에 저장되었습니다.")
            if args.output_video:
                print(f"처리된 영상이 '{args.output_video}'에 저장되었습니다.")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n처리가 사용자에 의해 중단되었습니다.")
        sys.exit(1)

    except Exception as e:
        print(f"\n오류 발생: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
