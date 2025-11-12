"""
Video Person Tracker - GUI Application
실시간 인물 추적 GUI 애플리케이션
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
from PIL import Image, ImageTk
import threading
import time
from realtime_tracker import RealtimePersonTracker
import json
from datetime import datetime


class PersonTrackerGUI:
    """인물 추적 GUI 애플리케이션"""

    def __init__(self, root):
        self.root = root
        self.root.title("Video Person Tracker - 실시간 인물 추적")
        self.root.geometry("1200x800")

        # 트래커
        self.tracker = None
        self.current_video_source = None
        self.update_job = None

        # UI 초기화
        self.setup_ui()

        # 종료 핸들러
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 그리드 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)

        # 1. 왼쪽: 비디오 프리뷰
        self.setup_video_panel(main_container)

        # 2. 오른쪽: 컨트롤 및 통계
        self.setup_control_panel(main_container)

        # 3. 하단: 상태 표시줄
        self.setup_status_bar(main_container)

    def setup_video_panel(self, parent):
        """비디오 프리뷰 패널"""
        video_frame = ttk.LabelFrame(parent, text="📹 비디오 프리뷰", padding="10")
        video_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # 비디오 라벨
        self.video_label = ttk.Label(video_frame, text="비디오를 선택하거나 웹캠을 시작하세요",
                                     background="black", foreground="white",
                                     font=("Arial", 14))
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # 비디오 컨트롤
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_webcam = ttk.Button(control_frame, text="🎥 웹캠 시작",
                                     command=self.start_webcam, width=15)
        self.btn_webcam.pack(side=tk.LEFT, padx=2)

        self.btn_file = ttk.Button(control_frame, text="📁 파일 열기",
                                   command=self.open_file, width=15)
        self.btn_file.pack(side=tk.LEFT, padx=2)

        self.btn_stop = ttk.Button(control_frame, text="⏹ 중지",
                                   command=self.stop_tracking, width=15, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        self.btn_reset = ttk.Button(control_frame, text="🔄 리셋",
                                    command=self.reset_tracking, width=15)
        self.btn_reset.pack(side=tk.LEFT, padx=2)

    def setup_control_panel(self, parent):
        """컨트롤 및 통계 패널"""
        right_container = ttk.Frame(parent)
        right_container.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_container.rowconfigure(1, weight=1)
        right_container.columnconfigure(0, weight=1)

        # 설정 패널
        settings_frame = ttk.LabelFrame(right_container, text="⚙️ 설정", padding="10")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Frame Skip 설정
        ttk.Label(settings_frame, text="프레임 스킵:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.frame_skip_var = tk.IntVar(value=2)
        frame_skip_spinbox = ttk.Spinbox(settings_frame, from_=1, to=30,
                                        textvariable=self.frame_skip_var, width=10)
        frame_skip_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(settings_frame, text="(낮을수록 정확, 높을수록 빠름)").grid(
            row=0, column=2, sticky=tk.W, pady=2)

        # Tolerance 설정
        ttk.Label(settings_frame, text="인식 정확도:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tolerance_var = tk.DoubleVar(value=0.6)
        tolerance_scale = ttk.Scale(settings_frame, from_=0.4, to=0.8,
                                   variable=self.tolerance_var, orient=tk.HORIZONTAL)
        tolerance_scale.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)

        self.tolerance_label = ttk.Label(settings_frame, text="0.60")
        self.tolerance_label.grid(row=1, column=3, sticky=tk.W, pady=2)

        def update_tolerance_label(*args):
            self.tolerance_label.config(text=f"{self.tolerance_var.get():.2f}")

        self.tolerance_var.trace('w', update_tolerance_label)

        # 통계 패널
        stats_frame = ttk.LabelFrame(right_container, text="📊 실시간 통계", padding="10")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        stats_frame.rowconfigure(1, weight=1)
        stats_frame.columnconfigure(0, weight=1)

        # 요약 정보
        summary_frame = ttk.Frame(stats_frame)
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.label_total_persons = ttk.Label(summary_frame, text="감지된 인물: 0명",
                                            font=("Arial", 12, "bold"))
        self.label_total_persons.pack(anchor=tk.W)

        self.label_current_frame = ttk.Label(summary_frame, text="현재 프레임: 0",
                                            font=("Arial", 10))
        self.label_current_frame.pack(anchor=tk.W)

        self.label_fps = ttk.Label(summary_frame, text="처리 속도: 0 FPS",
                                   font=("Arial", 10))
        self.label_fps.pack(anchor=tk.W)

        # 인물 목록
        ttk.Label(stats_frame, text="인물별 출연 횟수:",
                 font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(5, 2))

        # 스크롤 가능한 텍스트 영역
        self.person_list = scrolledtext.ScrolledText(stats_frame, height=15, width=40,
                                                     font=("Courier", 9))
        self.person_list.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.person_list.config(state=tk.DISABLED)

        # 결과 저장 버튼
        btn_save = ttk.Button(stats_frame, text="💾 결과 저장",
                             command=self.save_results, width=20)
        btn_save.grid(row=3, column=0, pady=(10, 0))

    def setup_status_bar(self, parent):
        """상태 표시줄"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        self.status_label = ttk.Label(status_frame, text="준비", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def start_webcam(self):
        """웹캠 시작"""
        if self.tracker and self.tracker.is_running():
            messagebox.showwarning("경고", "이미 실행 중입니다. 먼저 중지해주세요.")
            return

        try:
            self.current_video_source = 0
            self.start_tracking()
            self.update_status("웹캠 실행 중...")
        except Exception as e:
            messagebox.showerror("오류", f"웹캠을 시작할 수 없습니다: {e}")

    def open_file(self):
        """비디오 파일 열기"""
        if self.tracker and self.tracker.is_running():
            messagebox.showwarning("경고", "이미 실행 중입니다. 먼저 중지해주세요.")
            return

        file_path = filedialog.askopenfilename(
            title="비디오 파일 선택",
            filetypes=[
                ("비디오 파일", "*.mp4 *.avi *.mov *.mkv"),
                ("모든 파일", "*.*")
            ]
        )

        if file_path:
            try:
                self.current_video_source = file_path
                self.start_tracking()
                self.update_status(f"파일 처리 중: {file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"파일을 열 수 없습니다: {e}")

    def start_tracking(self):
        """추적 시작"""
        if not self.current_video_source:
            return

        # 트래커 생성
        self.tracker = RealtimePersonTracker(
            frame_skip=self.frame_skip_var.get(),
            tolerance=self.tolerance_var.get()
        )

        # 추적 시작
        self.tracker.start(
            video_source=self.current_video_source,
            frame_callback=self.on_frame_update,
            stats_callback=self.on_stats_update
        )

        # UI 업데이트
        self.btn_webcam.config(state=tk.DISABLED)
        self.btn_file.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        # 프레임 업데이트 시작
        self.last_update_time = time.time()
        self.frame_count_for_fps = 0
        self.update_video_display()

    def stop_tracking(self):
        """추적 중지"""
        if self.tracker:
            self.tracker.stop()

        # UI 업데이트
        self.btn_webcam.config(state=tk.NORMAL)
        self.btn_file.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

        self.update_status("중지됨")

        # 업데이트 취소
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None

    def reset_tracking(self):
        """추적 데이터 리셋"""
        if self.tracker and self.tracker.is_running():
            response = messagebox.askyesno("확인", "실행 중인 추적을 중지하고 데이터를 리셋하시겠습니까?")
            if response:
                self.stop_tracking()
            else:
                return

        if self.tracker:
            self.tracker.reset()

        # UI 리셋
        self.video_label.config(image='', text="비디오를 선택하거나 웹캠을 시작하세요")
        self.label_total_persons.config(text="감지된 인물: 0명")
        self.label_current_frame.config(text="현재 프레임: 0")
        self.label_fps.config(text="처리 속도: 0 FPS")
        self.person_list.config(state=tk.NORMAL)
        self.person_list.delete(1.0, tk.END)
        self.person_list.config(state=tk.DISABLED)

        self.update_status("리셋 완료")

    def on_frame_update(self, frame):
        """프레임 업데이트 콜백"""
        # 이 함수는 별도 스레드에서 호출되므로 실제 UI 업데이트는 update_video_display에서 처리
        pass

    def on_stats_update(self, stats):
        """통계 업데이트 콜백"""
        # 이 함수는 별도 스레드에서 호출되므로 실제 UI 업데이트는 update_video_display에서 처리
        pass

    def update_video_display(self):
        """비디오 디스플레이 업데이트 (메인 스레드)"""
        if not self.tracker or not self.tracker.is_running():
            return

        try:
            # 현재 프레임 가져오기
            frame = self.tracker.get_current_frame()

            if frame is not None:
                # OpenCV BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # PIL Image로 변환
                image = Image.fromarray(frame_rgb)

                # 크기 조정 (비율 유지)
                display_width = 800
                display_height = 600
                image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)

                # PhotoImage로 변환
                photo = ImageTk.PhotoImage(image)

                # 라벨 업데이트
                self.video_label.config(image=photo, text='')
                self.video_label.image = photo  # 참조 유지

                # FPS 계산
                self.frame_count_for_fps += 1
                current_time = time.time()
                if current_time - self.last_update_time >= 1.0:
                    fps = self.frame_count_for_fps / (current_time - self.last_update_time)
                    self.label_fps.config(text=f"처리 속도: {fps:.1f} FPS")
                    self.last_update_time = current_time
                    self.frame_count_for_fps = 0

            # 통계 업데이트
            stats = self.tracker.get_stats()
            self.update_statistics(stats)

            # 다음 업데이트 예약 (30ms 후)
            self.update_job = self.root.after(30, self.update_video_display)

        except Exception as e:
            print(f"디스플레이 업데이트 오류: {e}")
            self.update_job = self.root.after(30, self.update_video_display)

    def update_statistics(self, stats):
        """통계 정보 업데이트"""
        # 총 인물 수
        self.label_total_persons.config(text=f"감지된 인물: {stats['total_persons']}명")

        # 현재 프레임
        self.label_current_frame.config(text=f"현재 프레임: {stats['frame_count']}")

        # 인물 목록
        self.person_list.config(state=tk.NORMAL)
        self.person_list.delete(1.0, tk.END)

        person_data = stats['person_data']
        if person_data:
            # 출연 횟수로 정렬
            sorted_persons = sorted(person_data.items(),
                                   key=lambda x: x[1]['appearances'],
                                   reverse=True)

            for person_id, data in sorted_persons:
                line = f"{person_id}: {data['appearances']:4d}회"
                if data['first_seen'] is not None:
                    line += f" (프레임 {data['first_seen']}-{data['last_seen']})"
                self.person_list.insert(tk.END, line + "\n")
        else:
            self.person_list.insert(tk.END, "아직 감지된 인물이 없습니다.")

        self.person_list.config(state=tk.DISABLED)

    def save_results(self):
        """결과 저장"""
        if not self.tracker:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return

        stats = self.tracker.get_stats()
        if stats['total_persons'] == 0:
            messagebox.showwarning("경고", "감지된 인물이 없습니다.")
            return

        # 파일 저장 대화상자
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"tracking_results_{timestamp}.json"

        file_path = filedialog.asksaveasfilename(
            title="결과 저장",
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
        )

        if file_path:
            try:
                self.tracker.save_results(file_path)
                messagebox.showinfo("성공", f"결과가 저장되었습니다:\n{file_path}")
                self.update_status(f"결과 저장됨: {file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"결과 저장 실패: {e}")

    def update_status(self, message):
        """상태 표시줄 업데이트"""
        self.status_label.config(text=message)

    def on_closing(self):
        """프로그램 종료"""
        if self.tracker and self.tracker.is_running():
            response = messagebox.askyesno("확인", "추적이 실행 중입니다. 종료하시겠습니까?")
            if not response:
                return

            self.tracker.stop()

        self.root.destroy()


def main():
    """메인 함수"""
    root = tk.Tk()

    # 테마 적용 시도
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
        root.title("Video Person Tracker - 실시간 인물 추적")
        root.geometry("1200x800")
    except ImportError:
        pass  # 기본 테마 사용

    app = PersonTrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
