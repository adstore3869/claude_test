"""
Real-time Video Person Tracker
실시간 영상 인물 추적 모듈 (멀티스레딩 지원)
"""

import cv2
import face_recognition
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Callable
import threading
import queue
import time


class RealtimePersonTracker:
    """실시간 영상에서 인물을 추적하는 클래스"""

    def __init__(self, frame_skip: int = 2, tolerance: float = 0.6):
        """
        초기화

        Args:
            frame_skip: 몇 프레임마다 분석할지
            tolerance: 얼굴 인식 정확도
        """
        self.frame_skip = frame_skip
        self.tolerance = tolerance

        # 인물 데이터
        self.known_face_encodings = []
        self.known_face_ids = []
        self.person_data = defaultdict(lambda: {
            'appearances': 0,
            'frames': [],
            'first_seen': None,
            'last_seen': None,
            'last_location': None
        })

        self.next_person_id = 0
        self.frame_count = 0

        # 스레드 제어
        self.running = False
        self.thread = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue(maxsize=2)

        # 콜백
        self.frame_callback = None
        self.stats_callback = None

        # 현재 프레임 캐시
        self.current_frame = None
        self.current_frame_with_boxes = None
        self.lock = threading.Lock()

    def _identify_or_register_person(self, face_encoding: np.ndarray, frame_number: int) -> int:
        """얼굴 인코딩을 기존 인물과 비교하거나 새로운 인물로 등록"""
        if len(self.known_face_encodings) == 0:
            person_id = self.next_person_id
            self.known_face_encodings.append(face_encoding)
            self.known_face_ids.append(person_id)
            self.next_person_id += 1
            return person_id

        matches = face_recognition.compare_faces(
            self.known_face_encodings,
            face_encoding,
            tolerance=self.tolerance
        )

        face_distances = face_recognition.face_distance(
            self.known_face_encodings,
            face_encoding
        )

        if len(matches) > 0 and True in matches:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return self.known_face_ids[best_match_index]

        person_id = self.next_person_id
        self.known_face_encodings.append(face_encoding)
        self.known_face_ids.append(person_id)
        self.next_person_id += 1
        return person_id

    def _update_person_data(self, person_id: int, frame_number: int, location: Tuple):
        """인물 데이터 업데이트"""
        key = f"person_{person_id}"
        data = self.person_data[key]

        if data['first_seen'] is None:
            data['first_seen'] = frame_number

        data['last_seen'] = frame_number
        data['last_location'] = location

        if not data['frames'] or data['frames'][-1] != frame_number:
            data['frames'].append(frame_number)
            data['appearances'] += 1

    def _process_frame(self, frame: np.ndarray, frame_number: int) -> Tuple[np.ndarray, Dict]:
        """프레임을 처리하고 결과 반환"""
        # RGB 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 얼굴 감지
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # 결과 프레임 복사
        output_frame = frame.copy()

        # 현재 프레임의 인물들
        current_frame_persons = set()

        for face_location, face_encoding in zip(face_locations, face_encodings):
            person_id = self._identify_or_register_person(face_encoding, frame_number)

            if person_id not in current_frame_persons:
                self._update_person_data(person_id, frame_number, face_location)
                current_frame_persons.add(person_id)

            # 박스 그리기
            top, right, bottom, left = face_location

            # 색상 선택 (인물 ID에 따라 다른 색상)
            colors = [
                (0, 255, 0),    # 녹색
                (255, 0, 0),    # 파랑
                (0, 0, 255),    # 빨강
                (255, 255, 0),  # 시안
                (255, 0, 255),  # 마젠타
                (0, 255, 255),  # 노랑
            ]
            color = colors[person_id % len(colors)]

            # 얼굴 박스
            cv2.rectangle(output_frame, (left, top), (right, bottom), color, 2)

            # 배경 박스
            cv2.rectangle(output_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)

            # 텍스트
            font = cv2.FONT_HERSHEY_DUPLEX
            text = f"Person {person_id}"
            cv2.putText(output_frame, text, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

        # 통계 정보
        stats = {
            'total_persons': self.next_person_id,
            'persons_in_frame': len(current_frame_persons),
            'frame_number': frame_number,
            'person_data': dict(self.person_data)
        }

        return output_frame, stats

    def _processing_loop(self, video_source):
        """비디오 처리 루프 (별도 스레드에서 실행)"""
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            print("비디오를 열 수 없습니다.")
            self.running = False
            return

        frame_count = 0

        try:
            while self.running:
                ret, frame = cap.read()

                if not ret:
                    # 비디오 파일의 경우 끝에 도달하면 재시작
                    if isinstance(video_source, str):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        frame_count = 0
                        continue
                    else:
                        break

                # frame_skip에 따라 처리
                if frame_count % self.frame_skip == 0:
                    output_frame, stats = self._process_frame(frame, frame_count)

                    with self.lock:
                        self.current_frame = frame
                        self.current_frame_with_boxes = output_frame

                    # 콜백 호출
                    if self.frame_callback:
                        self.frame_callback(output_frame)

                    if self.stats_callback:
                        self.stats_callback(stats)
                else:
                    # 처리하지 않은 프레임도 표시
                    with self.lock:
                        self.current_frame = frame
                        if self.current_frame_with_boxes is None:
                            self.current_frame_with_boxes = frame

                    if self.frame_callback:
                        self.frame_callback(self.current_frame_with_boxes)

                frame_count += 1
                self.frame_count = frame_count

                # CPU 부하 감소
                time.sleep(0.01)

        finally:
            cap.release()
            self.running = False

    def start(self, video_source=0, frame_callback: Optional[Callable] = None,
              stats_callback: Optional[Callable] = None):
        """
        실시간 추적 시작

        Args:
            video_source: 비디오 소스 (0=웹캠, 또는 파일 경로)
            frame_callback: 프레임 업데이트 시 호출할 콜백 함수
            stats_callback: 통계 업데이트 시 호출할 콜백 함수
        """
        if self.running:
            print("이미 실행 중입니다.")
            return

        self.frame_callback = frame_callback
        self.stats_callback = stats_callback
        self.running = True

        self.thread = threading.Thread(
            target=self._processing_loop,
            args=(video_source,),
            daemon=True
        )
        self.thread.start()

    def stop(self):
        """추적 중지"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def get_current_frame(self) -> Optional[np.ndarray]:
        """현재 프레임 가져오기 (박스 포함)"""
        with self.lock:
            return self.current_frame_with_boxes.copy() if self.current_frame_with_boxes is not None else None

    def get_stats(self) -> Dict:
        """현재 통계 가져오기"""
        return {
            'total_persons': self.next_person_id,
            'frame_count': self.frame_count,
            'person_data': dict(self.person_data)
        }

    def reset(self):
        """추적 데이터 리셋"""
        self.known_face_encodings = []
        self.known_face_ids = []
        self.person_data = defaultdict(lambda: {
            'appearances': 0,
            'frames': [],
            'first_seen': None,
            'last_seen': None,
            'last_location': None
        })
        self.next_person_id = 0
        self.frame_count = 0

    def is_running(self) -> bool:
        """실행 중인지 확인"""
        return self.running

    def save_results(self, output_file: str = "realtime_results.json"):
        """결과를 JSON 파일로 저장"""
        import json

        # 직렬화 가능한 형태로 변환
        serializable_data = {}
        for key, value in self.person_data.items():
            serializable_data[key] = {
                'appearances': value['appearances'],
                'frames': value['frames'],
                'first_seen': value['first_seen'],
                'last_seen': value['last_seen']
            }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        print(f"결과가 {output_file}에 저장되었습니다.")
