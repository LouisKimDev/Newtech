import numpy as np
import cv2
from PIL import Image, ImageTk, ImageWin
import datetime
import os
import glob
import subprocess
import win32print
import win32ui
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from pynput import keyboard
import pygame

current_path = os.getcwd()

person_check = 0


class Application(ttk.Window):
    def __init__(self):
        super().__init__()
        style = Style(theme='vapor')
        style.configure('TButton', font=('Helvetica', 30, 'bold'))
        self.title("인생한컷")
        self.geometry("1920x1080")

        self.frames = {}
        self.captured_images = []  # 촬영된 이미지 경로를 저장하는 리스트

        # container 객체 지정, tkinter이용
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # frame에 각 페이지클래스의 컨테이너, self 객체 저장
        for F in (StartPage, ConfirmationPage, PersonConfigPage, PhotoPage, PoseRecommandPage, SelectionPage):
            # 각 페이지를 생성할 때 parent를 container로, controller을 self로 지정
            frame = F(container, self)
            # frames에 페이지 클래스를 key로, frame을 value로 저장
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if hasattr(frame, "on_show_frame"):
            frame.on_show_frame()  # 페이지가 화면에 표시될 때 특정 동작 수행


class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        container = ttk.Frame(self)
        container.pack(expand=True)

        btn_start = ttk.Button(container, text="촬영 시작하기", padding="80 60",
                               command=lambda: self.on_click_start(controller))
        btn_start.pack(pady=20)

    def on_click_start(self, controller):
        # 현재 디렉토리 절대경로를 입력받아서 yolo실행
        global current_path
        yolopath = current_path + "\\yolov7\\venv\\Scripts\\python.exe"
        yolocommand = [
            current_path + "\\yolov7\\detect.py",
            "--weights", "yolov7\yolov7.pt",
            "--conf", "0.25",
            "--img-size", "640",
            "--source", "1"
        ]
        subprocess.run([yolopath] + yolocommand)
        global person_check
        file_path = current_path + "\\person_count.txt"
        with open(file_path, "r") as file:
            person_check = file.read()
        file.close()
        controller.show_frame(ConfirmationPage)


class ReadyPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # 라벨에 큰 글꼴 크기 지정 및 중앙 배치
        self.label = tk.Label(self, text="인식중입니다. 5", font=("Helvetica", 20))
        self.label.pack(expand=True)

    def on_show_frame(self):
        self.countdown(5, self.controller)  # 기다리는 초 숫자 수정

        # 변경점 아래 5줄
        global person_check
        global current_path
        file_path = current_path + "\\person_count.txt"
        with open(file_path, "r") as file:
            person_check = file.read()
        file.close()

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

        self.lbl_question = tk.Label(
            container, text="", font=("Helvetica", 30, 'bold'))
        self.lbl_question.grid(row=0, column=0, columnspan=2)

        btn_yes = ttk.Button(container, text="YES", padding="40 30",
                             command=lambda: controller.show_frame(PoseRecommandPage))
        btn_yes.grid(row=1, column=0, padx=10, pady=10)

        btn_no = ttk.Button(container, text="NO", padding="50 30",
                            command=lambda: controller.show_frame(PersonConfigPage))
        btn_no.grid(row=1, column=1, padx=10, pady=10)

    def on_show_frame(self):
        global person_check
        self.lbl_question.config(text=f"{person_check} 명이 맞나요?")


# 만약 객체인식이 틀리면 수정하는 페이지
class PersonConfigPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        container = tk.Frame(self)
        container.pack(expand=True)
        label = tk.Label(container,
                         text='현재 인원 수를 선택해주세요',
                         font=('Helvetica', 30, 'bold'))
        label.pack()

        # 인원수 버튼 컨테이너
        buttons_frame = ttk.Frame(container)

        # 확인 버튼 컨테이너
        next_frame = ttk.Frame(container)

        # 1 ~ 4명의 버튼 생성
        for i in range(4):
            button = ttk.Button(buttons_frame, text=f'{i+1}명',
                                command=lambda i=i: self.on_click_num(controller, i+1))
            button.grid(row=i//2, column=i % 2, padx=10, pady=10)
        buttons_frame.pack()
        # 다음 페이지로 넘어가는 버튼 생성
        next_button = ttk.Button(next_frame, text='확인',
                                 command=lambda: controller.show_frame(PoseRecommandPage))
        next_button.grid(padx=10, pady=10)
        next_frame.pack()

    # 누른 버튼에 따라 person_count.txt 내용 수정
    def on_click_num(self, controller, person_num):
        global current_path
        print(f'{person_num}명 클릭 됨')
        file_path = current_path + "\\person_count.txt"
        with open(file_path, "w") as file:
            file.write(f'{person_num}')


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
                         font=("Helvetica", 30, 'bold'))
        label.pack()

        # 이미지 버튼을 배치하기 위한 프레임 생성 및 배치
        buttons_frame = ttk.Frame(container)
        buttons_frame.pack(expand=True)

        # 예시 이미지 파일 경로
        global current_path
        iamge_paths = [current_path + '\\assets\\pose1.png', current_path + '\\assets\\pose2.png',
                       current_path + '\\assets\\pose3.png', current_path + '\\assets\\pose4.png',
                       current_path + '\\assets\\pose5.png', current_path + '\\assets\\pose6.png']

        # 이미지 객체를 저장할 리스트
        self.images = []

        # 각 이미지 경로에 대해 반복
        for i, path in enumerate(iamge_paths):
            try:
                # 이미지 파일을 열고 크기 조정
                image = Image.open(path)
                image = image.resize((480, 240), Image.ADAPTIVE)

                # PhotoImage 객체 생성
                photo = ImageTk.PhotoImage(image)

                # 버튼 위젯 생성 및 이미지 할당
                button = ttk.Button(buttons_frame, image=photo,
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
            self.controller.frames[PhotoPage].selected_poses.append(
                self.selected_images)
            print(f"{path} 버튼이 클릭됨")

        if len(self.selected_images) == 6:  # 포즈 6개 선택
            # print("선택된 이미지 경로: ", self.selected_images)
            # print("photopage의 selected poses: ",
            #       self.controller.frames[PhotoPage].selected_poses)
            self.controller.show_frame(PhotoPage)


class PhotoPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        container = tk.Frame(self)
        container.pack(expand=True)

        self.imgCount = 0
        self.controller = controller
        self.selected_poses = []
        self.caputreCount = 0

        pygame.mixer.init()

        # 키보드 리스너 시작
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # 웹캠 초기화, 프레임 크기 설정
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if not self.camera.isOpened():
            raise ValueError("Unable to open video source", 0)

        # 화면에 비디오를 표시할 캔버스 생성
        self.vid = MyVideoCapture(self.camera)

        self.canvas = ttk.Canvas(
            self, width=self.vid.width, height=self.vid.height
        )
        self.canvas.pack(expand=True, anchor=CENTER)

        # 비디오 프레임 속도 및 업데이트 간격 설정
        self.fps = self.camera.get(cv2.CAP_PROP_FPS)
        self.delay = round(1000 / self.fps)

        # 비디오 프레임 업데이트 함수
        self.update()

    def update_captured_images_list(self):
        # 최신 6개의 이미지 파일을 가져옵니다.
        global current_path
        image_files = sorted(glob.glob(current_path + '\\images\\*.png'),
                             key=os.path.getmtime, reverse=True)[:6]
        self.controller.captured_images = image_files

    # 키보드 입력 감지해서 화면 캡쳐
    def on_press(self, key):
        global current_path
        audio_file = current_path + "\\assets\\shutter_sound.mp3"

        if str(key) == "Key.enter":
            sound = pygame.mixer.Sound(audio_file)
            sound.play()
            save_directory = "./images"  # 여기에 저장할 디렉토리 경로를 지정하세요
            current_datetime = datetime.datetime.now()
            filename = current_datetime.strftime(f"{self.imgCount+1}.png")
            file_path = os.path.join(save_directory, filename)
            # 카메라에서 현재 프레임 캡처
            ret, frame = self.camera.read()
            if ret:
                # 지정한 경로에 이미지 저장
                cv2.imwrite(file_path, frame)
                print("이미지가 저장되었습니다:", file_path)
                self.imgCount += 1   # 촬영한 사진 횟수 증가
                if self.imgCount >= 6:  # 여섯 장째 촬영했을 경우, 다음 화면으로 이동(사진 선택)
                    self.update_captured_images_list()
                    self.controller.show_frame(SelectionPage)

    def update(self):
        # 비디오 프레임 업데이트 함수
        ret, frame = self.vid.get_frame()

        if ret:
            # OpenCV 프레임을 RGB로 변환
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2RGB)

            # 선택된 포즈 이미지를 캡쳐한 프레임에 차례로 bitwise_or 연산 수행
            try:
                if len(self.selected_poses) >= 6:   # 포즈 3개 선택 -> 6개로 수정
                    pose_image = cv2.imread(
                        self.selected_poses[0][self.imgCount])
                    pose_image = cv2.resize(
                        pose_image, (1920, 1080))  # 웹캠 프레임 크기에 맞게 조절
                    frame = cv2.bitwise_or(frame, pose_image)
            except:
                pass

            frame = cv2.flip(frame, 1)

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
        self.selected_images = []

        # 초기 숫자 이미지 목록
        global current_path
        self.initial_number_images = [current_path + '\\assets\\01.png', current_path +
                                      '\\assets\\02.png', current_path + '\\assets\\03.png', current_path + '\\assets\\04.png']
        self.available_number_images = self.initial_number_images.copy()
        self.image_selection_status = {}

    def on_show_frame(self):
        # 이전에 생성된 이미지 라벨들을 제거합니다.
        for label in self.image_labels:
            label.destroy()
            self.image_labels.clear()

        # 새로운 이미지 라벨들을 생성합니다.
        self.create_widgets()

    # 촬영한 사진 보여주는 함수
    def create_widgets(self):
        # 이미지를 담을 새로운 프레임 생성
        images_container = tk.Frame(self)
        images_container.pack(side="top", expand=True)

        images_frame_top = tk.Frame(images_container)
        images_frame_top.pack(side="top", expand=True)

        # 간격 조절을 위해 pady 값을 조정
        images_frame_bottom = tk.Frame(images_container)
        images_frame_bottom.pack(side="top", expand=True, pady=5)

        image_files = sorted(self.controller.captured_images,
                             key=lambda f: os.path.basename(f))
        print(image_files)  # 파일 경로 출력

        self.image_labels = []
        for idx, file in enumerate(image_files):
            try:
                img = Image.open(file)
                img.thumbnail((320, 180))
                photo = ImageTk.PhotoImage(img)

                # 상단 프레임 또는 하단 프레임에 이미지 라벨 추가
                if idx < 3:
                    parent_frame = images_frame_top
                else:
                    parent_frame = images_frame_bottom

                label = tk.Label(parent_frame, image=photo)
                label.image = photo
                label.index = idx  # 라벨에 인덱스 저장

                # lambda 함수에 idx 인자 추가
                label.bind("<Button-1>", lambda e, idx=idx,
                           file=file: self.select_image(idx, file))

                label.pack(side="left", padx=10)
                self.image_labels.append(label)
            except Exception as e:
                print(f"Error loading image {file}: {e}")

        # '인쇄' 버튼 생성 및 이벤트 바인딩
        self.print_button = ttk.Button(
            self, text="인쇄", command=self.print_image,
            padding="80 60")
        self.print_button.pack(side="bottom", pady=20)

    def select_image(self, selected_index, clicked_image_path):
        if clicked_image_path in self.image_selection_status and self.image_selection_status[clicked_image_path]:
            # 이미 선택된 이미지를 클릭한 경우, 선택 해제
            self.remove_overlay(selected_index, clicked_image_path)
            used_number_image = self.image_selection_status[clicked_image_path]
            self.available_number_images.append(
                used_number_image)  # 숫자 이미지를 사용 가능한 목록에 추가
            self.available_number_images.sort(
                key=lambda x: self.initial_number_images.index(x))  # 목록을 초기 순서대로 정렬
            self.image_selection_status[clicked_image_path] = None
        else:
            # 새로운 이미지를 선택한 경우
            if self.available_number_images:
                number_image_path = self.available_number_images.pop(
                    0)  # 사용 가능한 첫 번째 숫자 이미지 가져오기
                overlaid_image = self.overlay_number_on_image(
                    clicked_image_path, number_image_path)
                self.update_image_label(selected_index, overlaid_image)
                self.selected_images.append(clicked_image_path)
                self.image_selection_status[clicked_image_path] = number_image_path

    def insert_number_image_in_order(self, number_image_path):
        # 숫자 이미지를 원래 순서에 맞게 목록에 다시 삽입
        index = self.initial_number_images.index(number_image_path)
        if number_image_path not in self.available_number_images:
            self.available_number_images.insert(index, number_image_path)

    def remove_overlay(self, index, image_path):
        # 오버레이된 숫자를 제거하고 원본 이미지를 다시 로드합니다.
        original_image = Image.open(image_path)
        original_image.thumbnail((320, 180))
        photo = ImageTk.PhotoImage(original_image)
        label = self.image_labels[index]
        label.configure(image=photo)
        label.image = photo

    def overlay_number_on_image(self, base_image_path, number_image_path):
        # 기본 이미지와 숫자 이미지를 엽니다.
        base_image = Image.open(base_image_path).convert("RGBA")
        number_image = Image.open(number_image_path).convert("RGBA")

        # 기본 이미지의 크기에 맞춰 숫자 이미지를 조정합니다.
        bx, by = base_image.size
        resized_number_image = number_image.resize((bx, by), Image.ANTIALIAS)

        # 오버레이된 이미지를 생성합니다.
        overlaid_image = Image.new("RGBA", base_image.size)
        overlaid_image.paste(base_image, (0, 0))
        overlaid_image.alpha_composite(resized_number_image)

        return overlaid_image

    def update_image_label(self, index, overlaid_image):
        # 고정된 크기로 이미지를 조정합니다.
        resized_image = overlaid_image.resize((320, 180))

        # 이미지 라벨을 업데이트합니다.
        photo = ImageTk.PhotoImage(resized_image)

        # 해당 인덱스의 라벨을 찾아 업데이트합니다.
        label = self.image_labels[index]
        label.configure(image=photo)
        label.image = photo

    def print_image(self):
        if self.selected_image_path is not None:
            print(f"인쇄할 이미지: {self.selected_image_path}")

            # 인쇄 명령
            self.print_to_printer("Canon SELPHY CP1300 WS")

            self.delete_all_images()
        else:
            print("선택된 이미지가 없습니다.")

    def print_to_printer(self, printer_name):
        hprinter = win32print.OpenPrinter(printer_name)

        global current_path

        # mainimage.png를 엽니다.
        main_image = Image.open(current_path + "\\assets\\main_image.png")

        # 1.png, 2.png, 3.png, 4.png를 엽니다.
        image1 = Image.open(current_path + "\\images\\1.png")
        image2 = Image.open(current_path + "\\images\\2.png")
        image3 = Image.open(current_path + "\\images\\3.png")
        image4 = Image.open(current_path + "\\images\\4.png")

        # 각각의 사각형의 좌표를 정의합니다.
        rect1 = [(217, 66), (634, 343)]
        rect2 = [(646, 66), (1063, 343)]
        rect3 = [(217, 355), (634, 632)]
        rect4 = [(646, 355), (1063, 632)]

        # 각각의 사각형의 크기를 계산합니다.
        size1 = (417, 277)
        size2 = (417, 277)
        size3 = (417, 277)
        size4 = (417, 277)

        # 각각의 1.png, 2.png, 3.png, 4.png를 새로운 크기로 조정합니다.
        image1 = image1.resize(size1)
        image2 = image2.resize(size2)
        image3 = image3.resize(size3)
        image4 = image4.resize(size4)

        # 조정된 이미지를 mainimage.png 위에 얹습니다.
        main_image.paste(image1, rect1[0])
        main_image.paste(image2, rect2[0])
        main_image.paste(image3, rect3[0])
        main_image.paste(image4, rect4[0])

        # 결과 이미지를 저장합니다.
        main_image.save(current_path + "\\images\\result.png")

        try:
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            hDC.StartDoc(current_path + "\\images\\result.png")
            hDC.StartPage()

            dib = Image.open(current_path + "\\images\\result.png")
            dib = dib.convert("RGB")

            width, height = dib.size

            dib = ImageWin.Dib(dib)

            dib.draw(hDC.GetHandleOutput(), (0, 0, width, height))
            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()

        finally:
            win32print.ClosePrinter(hprinter)

    def delete_all_images(self):
        print("사진 삭제를 시작합니다.")
        files = glob.glob(current_path + "\\images\\*")
        for f in files:
            print(f"삭제: {f}")
            os.remove(f)
        print("모든 이미지가 삭제되었습니다.")


app = Application()
app.mainloop()
