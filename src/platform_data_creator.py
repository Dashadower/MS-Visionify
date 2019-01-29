# -*- coding:utf-8 -*-
from screen_processor import StaticImageProcessor, MapleScreenCapturer
from terrain_analyzer import PathAnalyzer
import cv2, imutils, logging, threading
import tkinter as tk
from tkinter.constants import *
from PIL import Image, ImageTk
from tkinter.messagebox import showinfo, showerror, showwarning
from tkinter.filedialog import asksaveasfilename

class PlatformDataCaptureWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.wm_minsize(100, 30)
        self.resizable(0,0)
        self.focus_get()
        self.grab_set()
        self.title("데이터파일 생성기")

        self.screen_capturer = MapleScreenCapturer()
        self.image_processor = StaticImageProcessor(self.screen_capturer)
        self.terrain_analyzer = PathAnalyzer()
        self.image_label = tk.Label(self)
        self.image_label.pack(expand=YES, fill=BOTH)

        self.tool_frame = tk.Frame(self, borderwidth=2, relief=GROOVE)
        self.tool_frame.pack(expand=YES, fill=BOTH)
        self.image_processor.update_image(set_focus=False)
        self.minimap_rect = self.image_processor.get_minimap_rect()
        if not self.minimap_rect:
            self.image_label.configure(text="미니맵 찾을수 없음", fg="red")

        self.stopEvent = threading.Event()
        self.input_
        self.thread = threading.Thread(target=self.update_image, args=())
        self.thread.start()

    def update_image(self):
        while not self.stopEvent.is_set():
            self.image_processor.update_image(set_focus=False)
            if not self.minimap_rect:

                self.image_label.configure(text="미니맵 찾을수 없음", fg="red")
                self.minimap_rect = self.image_processor.get_minimap_rect()
                continue

            playerpos = self.image_processor.find_player_minimap_marker(self.minimap_rect)
            if not playerpos:
                self.image_label.configure(text="플레이어 위치 찾을수 없음", fg="red")
                continue

            cropped_img = cv2.cvtColor(self.image_processor.bgr_img[self.minimap_rect[1]:self.minimap_rect[1] + self.minimap_rect[3], self.minimap_rect[0]:self.minimap_rect[0] + self.minimap_rect[2]], cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cropped_img)
            img_tk = ImageTk.PhotoImage(image=img)
            self.image_label.image = img_tk
            self.image_label.configure(image=img_tk)
            self.update()



def create_platform_file(file_name):
    default_logger = logging.getLogger("platform_file_creator")
    default_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler("logging.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    default_logger.addHandler(fh)

    try:
        wincap = MapleScreenCapturer()
        scrp = StaticImageProcessor(wincap)
        scrp.update_image(set_focus=False)
        area = scrp.get_minimap_rect()
        pathextractor = PathAnalyzer()
        input_mode = 1
        while True:
            scrp.update_image(set_focus=False)
            print("R2")
            if not area == 0:
                playerpos = scrp.find_player_minimap_marker(area)

                if playerpos != 0:
                    if input_mode == 1:
                        pathextractor.input(playerpos[0], playerpos[1])
                    else:
                        pathextractor.input_oneway_platform(playerpos[0], playerpos[1])

                cropped_img = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]
                if playerpos != 0:
                    cv2.circle(cropped_img, playerpos, 3, (0, 0, 255), -1)
                if pathextractor.platforms or pathextractor.oneway_platforms:
                    for key, platform in pathextractor.platforms.items():
                        cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(0,255,0), 1)
                    for key, platform in pathextractor.oneway_platforms.items():
                        cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(255,0,0), 1)

                cropped_img = imutils.resize(cropped_img, width=500)

                cv2.imshow("pdc-screencap",cropped_img)

            inp = cv2.waitKey(1)


            if inp == ord('q'):
                cv2.destroyWindow("pdc-screencap")
                break
            elif inp == ord("r"):
                scrp.reset_minimap_area()
                area = scrp.get_minimap_rect()
                pathextractor.reset()

            elif inp == ord("o"):
                input_mode *= -1

            elif inp == ord("s"):
                pathextractor.save(file_name, area)
                break
    except:
        default_logger.exception("exception if platform data creator")

if __name__ == "__main__":
    root = tk.Tk()
    PlatformDataCaptureWindow()
    root.mainloop()