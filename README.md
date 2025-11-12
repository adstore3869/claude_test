# Video Person Tracking System

영상에서 인물을 분석하고 각 인물의 출연 횟수를 기록하는 프로그램입니다.

## 🎯 주요 기능

- **실시간 영상 분석**: 웹캠 또는 영상 파일에서 실시간으로 인물 추적
- **GUI 인터페이스**: 사용하기 쉬운 그래픽 사용자 인터페이스
- **자동 인물 감지**: OpenCV와 face_recognition을 활용한 정확한 얼굴 인식
- **고유 ID 부여**: 각 인물에게 자동으로 고유 ID 할당
- **출연 횟수 카운팅**: 실시간으로 각 인물의 출연 횟수 추적
- **실시간 통계**: 인물별 출연 횟수와 시간 정보 실시간 표시
- **결과 저장**: JSON 형식으로 분석 결과 저장
- **시각화**: 비디오 프리뷰에 인물 박스와 ID 표시

## 설치

```bash
pip install -r requirements.txt
```

## 🚀 빠른 시작

### 방법 1: GUI 애플리케이션 (추천)

가장 쉽고 직관적인 방법입니다!

**Windows:**
```bash
run_gui.bat
```

**Linux/Mac:**
```bash
./run_gui.sh
```

또는:
```bash
python run_gui.py
```

### 방법 2: 명령줄 인터페이스 (CLI)

```bash
# 웹캠으로 실시간 추적 (GUI 없이)
python cli.py -i 0

# 비디오 파일 분석
python cli.py -i your_video.mp4

# 성능 최적화 (5프레임마다 분석)
python cli.py -i your_video.mp4 --frame-skip 5 --output-video output.mp4
```

### 방법 3: Python API

```python
from video_person_tracker import VideoPersonTracker

# 트래커 초기화
tracker = VideoPersonTracker()

# 영상 분석
results = tracker.process_video("input_video.mp4")

# 결과 저장 및 출력
tracker.save_results("results.json")
tracker.print_summary()
```

### 방법 4: 실시간 추적 API

```python
from realtime_tracker import RealtimePersonTracker

# 실시간 트래커 생성
tracker = RealtimePersonTracker(frame_skip=2, tolerance=0.6)

# 웹캠으로 추적 시작
tracker.start(video_source=0)

# 또는 파일로 추적
# tracker.start(video_source="video.mp4")

# 통계 확인
stats = tracker.get_stats()
print(f"감지된 인물: {stats['total_persons']}명")

# 중지
tracker.stop()

# 결과 저장
tracker.save_results("results.json")
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

## 📋 GUI 기능

### 비디오 프리뷰
- 실시간 비디오 스트림 표시
- 감지된 인물에 색상별 박스 표시
- 각 인물의 ID 표시

### 컨트롤
- **웹캠 시작**: 웹캠으로 실시간 추적 시작
- **파일 열기**: 비디오 파일 선택 및 분석
- **중지**: 현재 추적 중지
- **리셋**: 추적 데이터 초기화

### 설정
- **프레임 스킵**: 처리 속도 조절 (1-30)
- **인식 정확도**: 얼굴 인식 민감도 조절 (0.4-0.8)

### 실시간 통계
- 감지된 총 인물 수
- 현재 프레임 번호
- 처리 속도 (FPS)
- 인물별 출연 횟수 목록

### 결과 저장
- JSON 형식으로 분석 결과 저장
- 타임스탬프가 포함된 자동 파일명

## 🎬 스크린샷

GUI 인터페이스는 다음과 같은 구성요소를 포함합니다:
- 왼쪽: 비디오 프리뷰 및 컨트롤 버튼
- 오른쪽: 설정 옵션 및 실시간 통계
- 하단: 상태 표시줄

## 📦 프로젝트 구조

```
claude_test/
├── gui_app.py              # GUI 애플리케이션 (메인)
├── realtime_tracker.py     # 실시간 추적 모듈
├── video_person_tracker.py # 비디오 파일 처리 모듈
├── cli.py                  # 명령줄 인터페이스
├── run_gui.py              # GUI 실행 스크립트
├── run_gui.bat             # Windows 실행 파일
├── run_gui.sh              # Linux/Mac 실행 파일
├── example_usage.py        # 사용 예제
├── test_installation.py    # 설치 확인 스크립트
├── requirements.txt        # 의존성 목록
├── README.md               # 프로젝트 문서
└── TUTORIAL.md             # 상세 튜토리얼
```

## 💡 사용 팁

### 성능 최적화
- **프레임 스킵 조절**: 값이 높을수록 빠르지만 일부 프레임을 건너뜁니다
  - 실시간 웹캠: 2-3 권장
  - 파일 처리: 5-10 권장

- **해상도 조정**: 고해상도 영상은 처리 속도가 느릴 수 있습니다

### 인식 정확도
- **tolerance 0.5**: 매우 엄격 (같은 사람도 다르게 인식 가능)
- **tolerance 0.6**: 균형 잡힌 설정 (권장)
- **tolerance 0.7**: 느슨함 (다른 사람을 같게 인식 가능)

### 웹캠 사용
- 첫 실행 시 카메라 권한 허용 필요
- 밝은 조명 환경에서 더 정확한 인식
- 정면 얼굴이 가장 잘 인식됨

## 🔧 요구사항

- Python 3.7+
- OpenCV
- face_recognition
- dlib (face_recognition 의존성)
- Tkinter (Python 기본 내장)
- matplotlib (그래프 기능, 선택사항)
- ttkthemes (더 나은 UI 테마, 선택사항)

## ⚠️ 주의사항

- 처음 실행 시 dlib 모델을 자동으로 다운로드합니다
- 고해상도 영상은 처리 시간이 오래 걸릴 수 있습니다
- 웹캠 사용 시 다른 프로그램이 카메라를 사용 중이면 안 됩니다
- dlib 설치에 C++ 컴파일러가 필요할 수 있습니다

## 📚 추가 문서

- **TUTORIAL.md**: 상세한 사용 가이드 및 예제
- **example_usage.py**: Python API 사용 예제
- 온라인 문서: [GitHub Repository]
