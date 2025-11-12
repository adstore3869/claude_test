# Video Person Tracking System

영상에서 인물을 분석하고 각 인물의 출연 횟수를 기록하는 프로그램입니다.

## 기능

- 영상 파일에서 인물 감지 및 인식
- 각 인물의 고유 ID 부여
- 영상에서 각 인물의 출연 횟수 카운트
- 결과를 JSON 파일로 저장
- 시각화된 결과 영상 생성 (옵션)

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 기본 사용

```python
from video_person_tracker import VideoPersonTracker

# 트래커 초기화
tracker = VideoPersonTracker()

# 영상 분석
results = tracker.process_video("input_video.mp4")

# 결과 저장
tracker.save_results("results.json")

# 결과 출력
tracker.print_summary()
```

### 고급 사용

```python
from video_person_tracker import VideoPersonTracker

# 설정 옵션
tracker = VideoPersonTracker(
    frame_skip=5,  # 5 프레임마다 분석 (성능 향상)
    tolerance=0.6,  # 얼굴 인식 정확도 (낮을수록 엄격)
    output_video=True  # 결과 영상 생성
)

# 영상 처리
results = tracker.process_video("input_video.mp4", output_path="output_video.mp4")

# 결과 확인
for person_id, data in results.items():
    print(f"Person {person_id}: {data['appearances']} appearances")
```

## 출력 형식

결과 JSON 파일 형식:

```json
{
  "person_0": {
    "appearances": 45,
    "first_seen": 120,
    "last_seen": 5400,
    "frames": [120, 125, 130, ...]
  },
  "person_1": {
    "appearances": 32,
    "first_seen": 300,
    "last_seen": 4800,
    "frames": [300, 305, 310, ...]
  }
}
```

## 요구사항

- Python 3.7+
- OpenCV
- face_recognition
- dlib (face_recognition 의존성)

## 주의사항

- 처음 실행 시 dlib 모델을 다운로드합니다
- 고해상도 영상은 처리 시간이 오래 걸릴 수 있습니다
- frame_skip 옵션으로 처리 속도를 조절할 수 있습니다
