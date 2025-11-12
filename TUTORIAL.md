# Video Person Tracker 튜토리얼

## 목차
1. [설치](#설치)
2. [기본 사용법](#기본-사용법)
3. [고급 기능](#고급-기능)
4. [성능 최적화](#성능-최적화)
5. [문제 해결](#문제-해결)

## 설치

### 1단계: 의존성 설치

```bash
pip install -r requirements.txt
```

**참고**: dlib 설치에 시간이 걸릴 수 있습니다. C++ 컴파일러가 필요합니다.

### 2단계: 설치 확인

```bash
python test_installation.py
```

모든 테스트가 통과하면 설치가 완료된 것입니다.

## 기본 사용법

### 방법 1: CLI 사용 (추천)

가장 간단한 방법입니다:

```bash
python cli.py -i your_video.mp4
```

결과는 `results.json` 파일에 저장됩니다.

### 방법 2: Python 스크립트 사용

```python
from video_person_tracker import VideoPersonTracker

# 트래커 생성
tracker = VideoPersonTracker()

# 영상 처리
tracker.process_video("your_video.mp4")

# 결과 저장 및 출력
tracker.save_results("results.json")
tracker.print_summary()
```

## 고급 기능

### 1. 결과 영상 생성

처리된 영상에 인물 박스와 ID를 표시합니다:

```bash
python cli.py -i input.mp4 --output-video output.mp4
```

또는 Python에서:

```python
tracker = VideoPersonTracker(output_video=True)
tracker.process_video("input.mp4", output_path="output.mp4")
```

### 2. 프레임 스킵으로 성능 향상

모든 프레임을 처리하는 대신 N 프레임마다 처리:

```bash
# 5프레임마다 처리 (약 5배 빠름)
python cli.py -i input.mp4 --frame-skip 5
```

```python
# Python에서
tracker = VideoPersonTracker(frame_skip=5)
```

### 3. 인식 정확도 조정

tolerance 값으로 얼굴 인식의 엄격함을 조정:

- **0.5**: 매우 엄격 (같은 사람도 다른 사람으로 인식될 수 있음)
- **0.6**: 기본값 (균형있는 설정)
- **0.7**: 느슨함 (다른 사람을 같은 사람으로 인식할 수 있음)

```bash
python cli.py -i input.mp4 --tolerance 0.5
```

### 4. 결과 분석

```python
from video_person_tracker import VideoPersonTracker
import json

# 영상 처리
tracker = VideoPersonTracker()
tracker.process_video("input.mp4")

# 특정 인물 정보 조회
person_0 = tracker.get_person_summary(0)
print(f"Person 0은 {person_0['appearances']}번 출연했습니다.")

# 결과 저장
tracker.save_results("results.json")

# JSON 파일 읽기
with open("results.json", "r") as f:
    data = json.load(f)

for person_id, info in data.items():
    print(f"{person_id}: {info['appearances']}회 출연")
```

## 성능 최적화

### 대용량 영상 처리

영상이 크거나 길 경우:

1. **프레임 스킵 증가**
   ```bash
   python cli.py -i large_video.mp4 --frame-skip 10
   ```

2. **출력 영상 생성 비활성화**
   ```bash
   python cli.py -i large_video.mp4 -o results.json
   # --output-video 옵션 제외
   ```

3. **영상 해상도 미리 줄이기**
   ```bash
   # ffmpeg 사용 예시
   ffmpeg -i input.mp4 -vf scale=640:360 input_small.mp4
   python cli.py -i input_small.mp4
   ```

### 처리 시간 비교

| 영상 길이 | frame_skip=1 | frame_skip=5 | frame_skip=10 |
|----------|--------------|--------------|---------------|
| 1분 (30fps) | ~5분 | ~1분 | ~30초 |
| 5분 (30fps) | ~25분 | ~5분 | ~2.5분 |
| 10분 (30fps) | ~50분 | ~10분 | ~5분 |

*실제 시간은 하드웨어 성능에 따라 다를 수 있습니다.*

## 결과 형식

`results.json` 파일 구조:

```json
{
  "person_0": {
    "appearances": 150,
    "first_seen": 0,
    "last_seen": 8950,
    "frames": [0, 5, 10, 15, ...]
  },
  "person_1": {
    "appearances": 89,
    "first_seen": 300,
    "last_seen": 7200,
    "frames": [300, 305, 310, ...]
  }
}
```

- **appearances**: 총 출연 횟수 (프레임 수)
- **first_seen**: 첫 출현 프레임 번호
- **last_seen**: 마지막 출현 프레임 번호
- **frames**: 출연한 모든 프레임 번호 리스트

## 문제 해결

### 1. dlib 설치 실패

**Windows:**
```bash
pip install cmake
pip install dlib
```

**Mac:**
```bash
brew install cmake
pip install dlib
```

**Linux:**
```bash
sudo apt-get install cmake
sudo apt-get install build-essential
pip install dlib
```

### 2. "얼굴을 찾을 수 없습니다"

- 영상의 화질이 너무 낮거나 얼굴이 작을 수 있습니다
- `tolerance` 값을 높여보세요 (예: 0.7)
- 영상 해상도를 확인하세요

### 3. 처리 속도가 너무 느림

- `frame_skip` 값을 증가시키세요 (5-10 권장)
- 영상 해상도를 줄이세요
- `output_video` 옵션을 비활성화하세요

### 4. 같은 사람이 여러 명으로 인식됨

- `tolerance` 값을 높이세요 (예: 0.65-0.7)
- 조명이 일정하지 않거나 각도 변화가 큰 경우 발생할 수 있습니다

### 5. 다른 사람이 같은 사람으로 인식됨

- `tolerance` 값을 낮추세요 (예: 0.5-0.55)
- 얼굴이 비슷한 경우 발생할 수 있습니다

## 활용 사례

### 1. 드라마/영화 분석

```python
tracker = VideoPersonTracker(frame_skip=30)  # 1초마다 분석
tracker.process_video("drama_episode1.mp4")
tracker.save_results("episode1_analysis.json")
```

### 2. 보안 영상 분석

```python
tracker = VideoPersonTracker(frame_skip=5, tolerance=0.55)
tracker.process_video("security_cam.mp4")
tracker.print_summary()
```

### 3. 유튜브 영상 분석

```python
# 여러 인물의 출연 시간 비교
tracker = VideoPersonTracker(frame_skip=10)
tracker.process_video("youtube_video.mp4")

for i in range(tracker.next_person_id):
    info = tracker.get_person_summary(i)
    if info:
        duration = info['last_seen'] - info['first_seen']
        print(f"Person {i}: {info['appearances']}회, {duration}프레임 동안 출연")
```

## 다음 단계

- 예제 코드를 수정하여 자신만의 분석 도구 만들기
- 결과 데이터를 시각화하는 스크립트 작성
- 웹캠 실시간 추적으로 확장

질문이나 문제가 있으면 GitHub Issues에 남겨주세요!
