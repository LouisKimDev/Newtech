import tkinter as tk
import cv2
from PIL import Image, ImageTk
import datetime
import os
import ttkbootstrap as ttk
from ttkbootstrap import Style
import glob
from PIL import Image, ImageTk
import win32print
import win32ui

class Application(ttk.Window):
    def __init__(self):
        super().__init__()
        style = Style(theme='minty')
        self.title("인생한컷")
        self.geometry("1280x720")

        self.frames = {}
        self.captured_images = []  # 촬영된 이미지 경로를 저장하는 리스트

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (StartPage, ReadyPage, ConfirmationPage, PhotoPage, PoseRecommandPage, SelectionPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if hasattr(frame, "on_show_frame"):
            frame.on_show_frame() # 페이지가 화면에 표시될 때 특정 동작 수행


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        container = tk.Frame(self)
        container.pack(expand=True)

        btn_start = tk.Button(container, text="촬영 시작하기", height=6, width=20,
                              font=("Helvetica", 20),
                              command=lambda: controller.show_frame(ReadyPage))
        btn_start.pack()


class ReadyPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # 라벨에 큰 글꼴 크기 지정 및 중앙 배치
        self.label = tk.Label(self, text="인식중입니다. 5", font=("Helvetica", 20))
        self.label.pack(expand=True)

    def on_show_frame(self):
        self.countdown(1, self.controller) # 기다리는 초 숫자 수정

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
                            command=lambda: controller.show_frame(PoseRecommandPage))
        btn_yes.grid(row=1, column=0)

        btn_no = tk.Button(container, text="NO", height=3,
                           font=("Helvetica", 20),
                           width=10, command=controller.quit)
        btn_no.grid(row=1, column=1)


class PoseRecommandPage(tk.Frame):
    def __init__(self, parent, controller):
        # 부모 클래스의 생성자를 호출하여 tk.Frame 초기화
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.selected_images = []

        # 이 프레임 안에 다른 위젯들을 포함할 컨테이너 프레임 생성
        container = tk.Frame(self)
        container.pack(expand=True)

        # 포즈 선택 안내를 위한 라벨 위젯 생성 및 배치
        label = tk.Label(container,
                         text='찍을 포즈를 선택해주세요',
                         width=20,
                         font=("Helvetica", 20))
        label.pack()

        # 이미지 버튼을 배치하기 위한 프레임 생성 및 배치
        buttons_frame = tk.Frame(container)
        buttons_frame.pack(expand=True)

        # 예시 이미지 파일 경로
        iamge_paths = ['./assets/pose1.png', './assets/pose2.png', './assets/pose3.png',
                       './assets/pose4.jpg', './assets/pose5.jpg', './assets/pose6.png']

        # 이미지 객체를 저장할 리스트
        self.images = []

        # 각 이미지 경로에 대해 반복
        for i, path in enumerate(iamge_paths):
            try:
                # 이미지 파일을 열고 크기 조정
                image = Image.open(path)
                image = image.resize((200, 200), Image.ADAPTIVE)

                # PhotoImage 객체 생성
                photo = ImageTk.PhotoImage(image)

                # 버튼 위젯 생성 및 이미지 할당
                button = tk.Button(buttons_frame, image=photo,
                                   command=lambda p=path: self.on_button_click(p))

                # 버튼에 이미지 객체 참조 유지
                button.image = photo

                # 버튼을 그리드 레이아웃에 배치
                button.grid(row=i//3, column=i % 3, padx=10, pady=10)

                # 생성된 PhotoImage 객체를 리스트에 저장
                self.images.append(photo)

            except IOError:
                print(f"이미지를 로드할 수 없습니다: {path}")

    # 버튼 클릭 이벤트 핸들러

    def on_button_click(self, path):
        if path not in self.selected_images:
            self.selected_images.append(path)
            print(f"{path} 버튼이 클릭됨")

        if len(self.selected_images) == 6:
            print("선택된 이미지 경로: ", self.selected_images)
            self.controller.show_frame(PhotoPage)


class PhotoPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        container = tk.Frame(self)
        container.pack(expand=True)
        self.imgCount = 0
        self.controller = controller

        # 웹캠 초기화, 프레임 크기 설정
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.camera.isOpened():
            raise ValueError("Unable to open video source", 0)

        # 캡쳐 버튼 생성
        self.capture_button = tk.Button(
            container, text='캡처', height=3, width=10,
            command=lambda: self.capture_image(controller)
        )
        self.capture_button.pack()

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

    def update_captured_images_list(self):
            # 최신 3개의 이미지 파일을 가져옵니다.
            image_files = sorted(glob.glob('./images/*.png'), key=os.path.getmtime, reverse=True)[:3]
            self.controller.captured_images = image_files

    def capture_image(self, controller):
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
            self.imgCount += 1   # 촬영한 사진 횟수 증가
            if self.imgCount >= 3: # 세 장째 촬영했을 경우, 다음 화면으로 이동(사진 선택)
                self.update_captured_images_list()
                self.controller.show_frame(SelectionPage)

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

# SelectionPage 클래스 추가
class SelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.selected_image_path = None
        self.selected_image_index = None  # 선택된 이미지 인덱스를 위한 속성 추가
        self.image_labels = []

    def on_show_frame(self):
        # 이전에 생성된 이미지 라벨들을 제거합니다.
        for label in self.image_labels:
            label.destroy()
            self.image_labels.clear()

        # 새로운 이미지 라벨들을 생성합니다.
        self.create_widgets()

    def create_widgets(self):
        images_frame = tk.Frame(self)
        images_frame.pack(side="top", expand=True)

        image_files = sorted(self.controller.captured_images, key=lambda f: os.path.basename(f))
        print(image_files)  # 파일 경로 출력

        self.image_labels = []
        for idx, file in enumerate(image_files):
            try:
                img = Image.open(file)
                img.thumbnail((250, 250))
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(images_frame, image=photo)
                label.image = photo
                label.index = idx  # 라벨에 인덱스 저장
                label.bind("<Button-1>", lambda e, file=file: self.select_image(file))
                label.pack(side="left", padx=10)
                self.image_labels.append(label)
            except Exception as e:
                print(f"Error loading image {file}: {e}")

        # '인쇄' 버튼 생성 및 이벤트 바인딩
        self.print_button = tk.Button(self, text="인쇄", height=3, width=10, 
                                      font=("Helvetica", 20), command=self.print_image)
        self.print_button.pack(side="bottom", pady=20)

    def select_image(self, clicked_image_path):
        self.selected_image_path = clicked_image_path
        print(f"선택된 이미지 경로: {self.selected_image_path}")

        # 모든 이미지 라벨의 테두리를 제거하고 선택된 이미지에 테두리를 추가합니다.
        #for i, label in enumerate(self.image_labels):
        for i, label in enumerate(reversed(self.image_labels)):
            label.config(borderwidth=0)
            if self.controller.captured_images[i] == clicked_image_path:
                label.config(borderwidth=2, relief="solid")
            

    def print_image(self):
        if self.selected_image_path is not None:
            print(f"인쇄할 이미지: {self.selected_image_path}")

            # 인쇄 명령

            self.delete_all_images()
        else:
            print("선택된 이미지가 없습니다.")

    def delete_all_images(self):
        print("사진 삭제를 시작합니다.")
        files = glob.glob('./images/*')
        for f in files:
            print(f"삭제: {f}")
            os.remove(f)
        print("모든 이미지가 삭제되었습니다.")

app = Application()
app.mainloop()
