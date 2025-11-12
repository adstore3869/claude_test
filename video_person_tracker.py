"""
Video Person Tracker
영상에서 인물을 감지하고 출연 횟수를 기록하는 모듈
"""

import cv2
import face_recognition
import numpy as np
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import os


class VideoPersonTracker:
    """영상에서 인물을 추적하고 출연 횟수를 기록하는 클래스"""

    def __init__(self, frame_skip: int = 1, tolerance: float = 0.6, output_video: bool = False):
        """
        초기화

        Args:
            frame_skip: 몇 프레임마다 분석할지 (1=모든 프레임, 5=5프레임마다)
            tolerance: 얼굴 인식 정확도 (0.6이 기본값, 낮을수록 엄격)
            output_video: 결과 영상 생성 여부
        """
        self.frame_skip = frame_skip
        self.tolerance = tolerance
        self.output_video = output_video

        # 인물 데이터 저장
        self.known_face_encodings = []
        self.known_face_ids = []
        self.person_data = defaultdict(lambda: {
            'appearances': 0,
            'frames': [],
            'first_seen': None,
            'last_seen': None
        })

        self.next_person_id = 0
        self.frame_count = 0

    def _get_face_encodings(self, frame: np.ndarray) -> Tuple[List, List]:
        """
        프레임에서 얼굴 위치와 인코딩을 추출

        Args:
            frame: 비디오 프레임

        Returns:
            얼굴 위치 리스트와 얼굴 인코딩 리스트
        """
        # RGB로 변환 (face_recognition 라이브러리는 RGB를 사용)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 얼굴 위치 찾기
        face_locations = face_recognition.face_locations(rgb_frame)

        # 얼굴 인코딩 추출
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        return face_locations, face_encodings

    def _identify_or_register_person(self, face_encoding: np.ndarray, frame_number: int) -> int:
        """
        얼굴 인코딩을 기존 인물과 비교하거나 새로운 인물로 등록

        Args:
            face_encoding: 얼굴 인코딩
            frame_number: 현재 프레임 번호

        Returns:
            인물 ID
        """
        if len(self.known_face_encodings) == 0:
            # 첫 번째 인물
            person_id = self.next_person_id
            self.known_face_encodings.append(face_encoding)
            self.known_face_ids.append(person_id)
            self.next_person_id += 1
            return person_id

        # 기존 인물과 비교
        matches = face_recognition.compare_faces(
            self.known_face_encodings,
            face_encoding,
            tolerance=self.tolerance
        )

        # 거리 계산
        face_distances = face_recognition.face_distance(
            self.known_face_encodings,
            face_encoding
        )

        if len(matches) > 0 and True in matches:
            # 가장 가까운 매치 찾기
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return self.known_face_ids[best_match_index]

        # 새로운 인물
        person_id = self.next_person_id
        self.known_face_encodings.append(face_encoding)
        self.known_face_ids.append(person_id)
        self.next_person_id += 1
        return person_id

    def _update_person_data(self, person_id: int, frame_number: int):
        """
        인물 데이터 업데이트

        Args:
            person_id: 인물 ID
            frame_number: 프레임 번호
        """
        data = self.person_data[f"person_{person_id}"]

        # 첫 출현 시간
        if data['first_seen'] is None:
            data['first_seen'] = frame_number

        # 마지막 출현 시간
        data['last_seen'] = frame_number

        # 프레임 기록
        if not data['frames'] or data['frames'][-1] != frame_number:
            data['frames'].append(frame_number)
            data['appearances'] += 1

    def process_video(self, video_path: str, output_path: Optional[str] = None) -> Dict:
        """
        영상을 처리하고 인물을 추적

        Args:
            video_path: 입력 영상 파일 경로
            output_path: 출력 영상 파일 경로 (옵션)

        Returns:
            인물별 출연 데이터 딕셔너리
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video_path}")

        # 영상 열기
        video_capture = cv2.VideoCapture(video_path)

        if not video_capture.isOpened():
            raise ValueError(f"영상을 열 수 없습니다: {video_path}")

        # 영상 정보
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"영상 정보: {width}x{height}, {fps} FPS, {total_frames} 프레임")

        # 출력 영상 설정
        video_writer = None
        if self.output_video and output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_number = 0
        processed_frames = 0

        try:
            while True:
                ret, frame = video_capture.read()

                if not ret:
                    break

                # frame_skip 설정에 따라 프레임 건너뛰기
                if frame_number % self.frame_skip == 0:
                    # 얼굴 감지 및 인코딩
                    face_locations, face_encodings = self._get_face_encodings(frame)

                    # 각 얼굴 처리
                    current_frame_persons = set()
                    for face_location, face_encoding in zip(face_locations, face_encodings):
                        # 인물 식별 또는 등록
                        person_id = self._identify_or_register_person(face_encoding, frame_number)

                        # 중복 카운트 방지 (같은 프레임에서 같은 사람)
                        if person_id not in current_frame_persons:
                            self._update_person_data(person_id, frame_number)
                            current_frame_persons.add(person_id)

                        # 영상에 표시
                        if video_writer:
                            top, right, bottom, left = face_location
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(
                                frame,
                                f"Person {person_id}",
                                (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                2
                            )

                    processed_frames += 1

                    # 진행상황 출력
                    if processed_frames % 10 == 0:
                        progress = (frame_number / total_frames) * 100
                        print(f"처리 중... {progress:.1f}% ({frame_number}/{total_frames} 프레임)")

                # 출력 영상에 프레임 쓰기
                if video_writer:
                    video_writer.write(frame)

                frame_number += 1
                self.frame_count = frame_number

        finally:
            video_capture.release()
            if video_writer:
                video_writer.release()

        print(f"\n처리 완료! 총 {len(self.person_data)}명의 인물을 감지했습니다.")

        return dict(self.person_data)

    def save_results(self, output_file: str = "results.json"):
        """
        결과를 JSON 파일로 저장

        Args:
            output_file: 출력 파일 경로
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.person_data, f, indent=2, ensure_ascii=False)

        print(f"결과가 {output_file}에 저장되었습니다.")

    def print_summary(self):
        """결과 요약 출력"""
        print("\n" + "="*50)
        print("인물 추적 결과 요약")
        print("="*50)

        if not self.person_data:
            print("감지된 인물이 없습니다.")
            return

        for person_id, data in sorted(self.person_data.items()):
            print(f"\n{person_id}:")
            print(f"  출연 횟수: {data['appearances']}회")
            print(f"  첫 출현: {data['first_seen']}번째 프레임")
            print(f"  마지막 출현: {data['last_seen']}번째 프레임")

            # 출연 시간 계산 (프레임 기반)
            if data['first_seen'] and data['last_seen']:
                duration = data['last_seen'] - data['first_seen']
                print(f"  출연 구간: {duration}프레임")

        print("\n" + "="*50)

    def get_person_summary(self, person_id: int) -> Optional[Dict]:
        """
        특정 인물의 정보 조회

        Args:
            person_id: 인물 ID

        Returns:
            인물 데이터 딕셔너리 또는 None
        """
        key = f"person_{person_id}"
        return self.person_data.get(key)
