import tkinter as tk
import cv2
from PIL import Image, ImageTk
import datetime
import os
import ttkbootstrap as ttk
from ttkbootstrap import Style


class Application(ttk.Window):
    def __init__(self):
        super().__init__()
        style = Style(theme='minty')  # ttkbootstrap 스타일 적용

        self.title("인생한컷")
        self.geometry("1280x720")
        self.frames = {}

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (StartPage, ReadyPage, ConfirmationPage, PhotoPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        container = tk.Frame(self)
        container.pack(expand=True)

        btn_start = tk.Button(container, text="촬영", height=6, width=20,
                              font=("Helvetica", 20),
                              command=lambda: controller.show_frame(ReadyPage))
        btn_start.pack()


class ReadyPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # 라벨에 큰 글꼴 크기 지정 및 중앙 배치
        self.label = tk.Label(self, text="인식중입니다. 5", font=("Helvetica", 20))
        self.label.pack(expand=True)

        # 카운트다운 시작
        self.countdown(6, controller)

    def countdown(self, count, controller):
        if count > 0:
            self.label.config(text=f"인식중입니다. {count}")
            self.after(1000, self.countdown, count-1, controller)
        else:
            controller.show_frame(ConfirmationPage)


class ConfirmationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        container = tk.Frame(self)
        container.pack(expand=True)

        lbl_question = tk.Label(
            container, text="N 명이 맞나요?", font=("Helvetica", 20))
        lbl_question.grid(row=0, column=0, columnspan=2)

        btn_yes = tk.Button(container, text="YES", height=3, width=10,
                            font=("Helvetica", 20),
                            command=lambda: controller.show_frame(PhotoPage))
        btn_yes.grid(row=1, column=0)

        btn_no = tk.Button(container, text="NO", height=3,
                           font=("Helvetica", 20),
                           width=10, command=controller.quit)
        btn_no.grid(row=1, column=1)


class PhotoPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        container = tk.Frame(self)
        container.pack(expand=True)

        # 캡쳐 버튼 생성
        self.capture_button = tk.Button(
            container, text='캡처', height=3, width=10,
            command=self.capture_image
        )
        self.capture_button.pack()

        # 웹캠 초기화, 프레임 크기 설정
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.camera.isOpened():
            raise ValueError("Unable to open video source", 0)

        # 화면에 비디오를 표시할 캔버스 생성
        self.vid = MyVideoCapture(self.camera)
        self.canvas = tk.Canvas(
            self, width=self.vid.width, height=self.vid.height
        )
        self.canvas.pack()

        # 비디오 프레임 속도 및 업데이트 간격 설정
        self.fps = self.camera.get(cv2.CAP_PROP_FPS)
        self.delay = round(1000 / self.fps)

        # 비디오 프레임 업데이트 함수
        self.update()

    def capture_image(self):
        # 파일 저장 디렉토리 및 파일명 설정
        save_directory = "./images"  # 여기에 저장할 디렉토리 경로를 지정하세요
        current_datetime = datetime.datetime.now()
        filename = current_datetime.strftime("%Y%m%d_%H%M%S.png")
        file_path = os.path.join(save_directory, filename)

        # 카메라에서 현재 프레임 캡처
        ret, frame = self.camera.read()
        if ret:
            # 지정한 경로에 이미지 저장
            cv2.imwrite(file_path, frame)
            print("이미지가 저장되었습니다:", file_path)

    def update(self):
        # 비디오 프레임 업데이트 함수
        ret, frame = self.vid.get_frame()

        if ret:
            # OpenCV 프레임을 RGB로 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # frame을 Tkinter 이미지로 변환 및 참조 저장
            self.photo = ImageTk.PhotoImage(
                image=Image.fromarray(frame)
            )

            # 캔버스에 이미지 표시
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.after(self.delay, self.update)

    def __del__(self):
        # 객체가 삭제될 때 녹화 중이면 비디오 파일 닫기
        self.camera.release()


class MyVideoCapture:
    def __init__(self, camera):
        # 비디오 캡쳐 객체 초기화
        self.camera = camera
        self.width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame(self):
        # 웹캠에서 현재 프레임 읽기
        ret, frame = self.camera.read()
        if ret:
            # 현재 시간을 표시할 텍스트 생성
            font_color = (255, 255, 255)
            font = cv2.FONT_HERSHEY_DUPLEX
            dt = datetime.datetime.now()
            dt = str(dt.strftime("%Y%m%d_%H%M%S"))
            frame = cv2.putText(frame, dt,
                                (30, 60),
                                font, 1, font_color, 4, cv2.LINE_AA)

            return (ret, frame)
        else:
            return (ret, None)

    def __del__(self):
        # 객체가 삭제될 때 웹캠 닫기
        self.camera.release()


app = Application()
app.mainloop()
