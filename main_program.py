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

# 현재 디렉토리 경로
current_path = os.getcwd()

# 객체인식으로 인식된 사람 수
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
        for F in (StartPage, ConfirmationPage, PersonConfigPage, ModeSelectPage, PhotoPage, PoseRecommandPage, SelectionPage):
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
                             command=lambda: controller.show_frame(ModeSelectPage))
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
            button.grid(row=i//2, column=i % 2, padx=20, pady=20)
        buttons_frame.pack()
        # 다음 페이지로 넘어가는 버튼 생성
        next_button = ttk.Button(next_frame, text='확인',
                                 command=lambda: controller.show_frame(ModeSelectPage))
        next_button.grid(padx=20, pady=20)
        next_frame.pack()

    # 누른 버튼에 따라 person_count.txt 내용 수정
    def on_click_num(self, controller, person_num):
        global current_path
        print(f'{person_num}명 클릭 됨')
        file_path = current_path + "\\person_count.txt"
        with open(file_path, "w") as file:
            file.write(f'{person_num}')


# 포즈 가이드, 배경 선택, 바닐라 모드 선택 페이지
class ModeSelectPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        container = tk.Frame(self)
        container.pack(expand=True)
        label = tk.Label(container,
                         text='원하는 모드를 선택해 주세요.',
                         font=('Helvetica', 30, 'bold'))
        label.pack()

        # 모드 선택 버튼 컨테이너
        buttons_frame = ttk.Frame(container)

        # 버튼 생성
        button1 = ttk.Button(buttons_frame, text='포즈 가이드 모드', padding="40 30",
                             command=lambda i=1: self.on_click_num(controller, i))
        button1.grid(row=0, column=0, padx=20, pady=20)

        button2 = ttk.Button(buttons_frame, text='배경 선택 모드', padding="50 30",
                             command=lambda i=2: self.on_click_num(controller, i))
        button2.grid(row=0, column=1, padx=20, pady=20)

        button3 = ttk.Button(buttons_frame, text='기본 모드', padding="80 30",
                             command=lambda i=3: self.on_click_num(controller, i))
        button3.grid(row=0, column=2, padx=20, pady=20)
        buttons_frame.pack()

    # 누른 버튼에 따라 person_count.txt 내용 수정

    def on_click_num(self, controller, mode_num):
        if mode_num == 1:
            controller.show_frame(PoseRecommandPage)
        elif mode_num == 2:
            pass
            # controller.show_frame(ChromakeyPage)
        elif mode_num == 3:
            controller.show_frame(PhotoPage)


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

    # 키보드 입력 감지해서 화면 캡쳐 및 크로마키 처리
    def on_press(self, key):
        global current_path
        audio_file = current_path + "\\assets\\shutter_sound.mp3"
        background_image_path = current_path + "\\assets\\chroma_key.jpg"  # 새 배경 이미지 파일 경로

        if str(key) == "Key.enter":
            sound = pygame.mixer.Sound(audio_file)
            sound.play()
            save_directory = current_path + "\\images"
            current_datetime = datetime.datetime.now()
            filename = current_datetime.strftime(f"{self.imgCount+1}.png")
            file_path = os.path.join(save_directory, filename)

            # 카메라에서 현재 프레임 캡처   
            ret, frame = self.camera.read()
            if ret:
                # 크로마키 처리
                frame = self.apply_chroma_key(frame, background_image_path)
                    #background_image_path 에 크로마키 입힐 사진(보라색)을 넣어야 함

                # 지정한 경로에 이미지 저장
                cv2.imwrite(file_path, frame)
                print("이미지가 저장되었습니다:", file_path)
                self.imgCount += 1
                if self.imgCount >= 6:
                    self.update_captured_images_list()
                    self.controller.show_frame(SelectionPage)

    # 크로마키 처리 함수
    def apply_chroma_key(self, frame, background_image_path):
        # 배경 이미지 불러오기
        background = cv2.imread(background_image_path)
        background = cv2.resize(background, (frame.shape[1], frame.shape[0]))

        # 초록색의 HSV 범위 정의
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([86, 255,255])

        # HSV 색상 공간으로 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 초록색 마스크 생성
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 마스크 반전 (초록색이 아닌 부분을 선택)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 마스크된 영역에서 크로마키 천의 영역만 배경 이미지로 대체
        background_applied = cv2.bitwise_and(background, background, mask=mask)

        # 마스크를 반전시켜 나머지 영역에는 원본 프레임을 유지
        mask_inv = cv2.bitwise_not(mask)
        foreground = cv2.bitwise_and(frame, frame, mask=mask_inv)

        # 마스크된 배경과 원본 프레임의 나머지 영역을 합성
        result = cv2.bitwise_or(background_applied, foreground)

        return result

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
        global current_path

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.selected_image_path = None
        self.selected_image_index = None
        self.image_labels = []
        self.selected_images = []
        self.selected_ordered_images = []

        self.initial_number_images = [current_path + '\\assets\\01.png', current_path + '\\assets\\02.png',
                                      current_path + '\\assets\\03.png', current_path + '\\assets\\04.png']
        self.available_number_images = self.initial_number_images.copy()
        self.image_selection_status = {}

        # 인쇄 버튼을 위한 컨테이너
        print_button_container = tk.Frame(self)
        print_button_container.pack(side="bottom", pady=0, expand=True)

        # 인쇄 버튼을 포함하는 프레임 생성
        print_button_frame = tk.Frame(self)
        print_button_frame.pack(side="bottom", fill=tk.X, pady=0)

        # 인쇄 버튼
        self.print_button = tk.Button(print_button_frame, text="인쇄", height=3, width=10,
                                      font=("Helvetica", 20), command=self.print_image,
                                      state=tk.DISABLED)
        self.print_button.pack(side="top", anchor="center")

        # 가이드 이미지를 포함하는 별도의 프레임 생성
        guide_image_frame = tk.Frame(self)
        guide_image_frame.pack(side="bottom", fill=tk.X)

        # 가이드 이미지
        guide_image_path = current_path + '\\assets\\guide_image.png'
        guide_img = Image.open(guide_image_path)
        guide_img = guide_img.resize((200, 130))
        guide_photo = ImageTk.PhotoImage(guide_img)
        guide_label = tk.Label(guide_image_frame, image=guide_photo)
        guide_label.image = guide_photo
        guide_label.pack(side="right", padx=500)

    def on_show_frame(self):
        for label in self.image_labels:
            label.destroy()
        self.image_labels.clear()
        self.create_widgets()

    def create_widgets(self):
        images_container = tk.Frame(self)
        images_container.pack(side="top", expand=True)

        images_frame_top = tk.Frame(images_container)
        images_frame_top.pack(side="top", expand=True)

        images_frame_bottom = tk.Frame(images_container)
        images_frame_bottom.pack(side="top", expand=True, pady=5)

        image_files = sorted(self.controller.captured_images,
                             key=lambda f: os.path.basename(f))
        print(image_files)

        self.image_labels = []
        for idx, file in enumerate(image_files):
            try:
                img = Image.open(file)
                img.thumbnail((320, 180))
                photo = ImageTk.PhotoImage(img)

                if idx < 3:
                    parent_frame = images_frame_top
                else:
                    parent_frame = images_frame_bottom

                label = tk.Label(parent_frame, image=photo)
                label.image = photo
                label.index = idx
                label.bind("<Button-1>", lambda e, idx=idx,
                           file=file: self.select_image(idx, file))
                label.pack(side="left", padx=10)
                self.image_labels.append(label)
            except Exception as e:
                print(f"Error loading image {file}: {e}")

    def select_image(self, selected_index, clicked_image_path):
        if clicked_image_path in self.image_selection_status and self.image_selection_status[clicked_image_path]:
            self.remove_overlay(selected_index, clicked_image_path)
            used_number_image = self.image_selection_status[clicked_image_path]
            self.available_number_images.append(used_number_image)
            self.available_number_images.sort(
                key=lambda x: self.initial_number_images.index(x))
            self.image_selection_status[clicked_image_path] = None
            self.selected_ordered_images.remove(clicked_image_path)
        else:
            if self.available_number_images:
                number_image_path = self.available_number_images.pop(0)
                overlaid_image = self.overlay_number_on_image(
                    clicked_image_path, number_image_path)
                self.update_image_label(selected_index, overlaid_image)
                self.selected_images.append(clicked_image_path)
                self.image_selection_status[clicked_image_path] = number_image_path
                self.selected_ordered_images.append(clicked_image_path)

        if len(self.selected_ordered_images) == 4:
            self.print_button.config(state=tk.NORMAL)
        else:
            self.print_button.config(state=tk.DISABLED)

    def remove_overlay(self, index, image_path):
        original_image = Image.open(image_path)
        original_image.thumbnail((320, 180))
        photo = ImageTk.PhotoImage(original_image)
        label = self.image_labels[index]
        label.configure(image=photo)
        label.image = photo

    def overlay_number_on_image(self, base_image_path, number_image_path):
        base_image = Image.open(base_image_path).convert("RGBA")
        number_image = Image.open(number_image_path).convert("RGBA")

        by = base_image.size[1]
        resized_number_image = number_image.resize(
            (by, by), Image.Resampling.LANCZOS)

        bx_center = base_image.size[0] // 2
        position = (bx_center - by // 2, 0)

        overlaid_image = Image.new("RGBA", base_image.size)
        overlaid_image.paste(base_image, (0, 0))
        overlaid_image.alpha_composite(resized_number_image, position)

        return overlaid_image

    def update_image_label(self, index, overlaid_image):
        resized_image = overlaid_image.resize((320, 180))
        photo = ImageTk.PhotoImage(resized_image)
        label = self.image_labels[index]
        label.configure(image=photo)
        label.image = photo

    def print_image(self):
        print("인쇄시작")
        if len(self.selected_ordered_images) == 4:
            self.print_to_printer("Canon SELPHY CP1300 WS")
            # self.delete_all_images()
        else:
            print("선택된 이미지가 없습니다.")

    def print_to_printer(self, printer_name):
        global current_path
        hprinter = win32print.OpenPrinter(printer_name)

        main_image = Image.open(current_path + "\\assets\\main_image.png")

        selected_images = self.controller.frames[SelectionPage].selected_ordered_images

        rects = [(208, 113), (646, 113), (208, 365), (646, 365)]
        size = (426, 240)  # 1280x720 / 3

        for idx, selected_image in enumerate(selected_images):
            image = Image.open(selected_image)
            image = image.resize(size)
            main_image.paste(image, rects[idx])  # rects 리스트에서 위치를 가져옵니다.

        dpi = 300
        size_pixels = (int(5.9 * dpi), int(3.833 * dpi))

        # 지정된 크기로 조정
        main_image = main_image.resize(size_pixels, Image.Resampling.LANCZOS)

        # 조정된 이미지를 저장
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
        global current_path
        print("사진 삭제를 시작합니다.")
        files = glob.glob(current_path + '\\images\*')
        for f in files:
            print(f"삭제: {f}")
            os.remove(f)
        print("모든 이미지가 삭제되었습니다.")


app = Application()
app.mainloop()
