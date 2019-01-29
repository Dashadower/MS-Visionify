# -*- coding:utf-8 -*-
import logging
default_logger = logging.getLogger("main")
default_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler("logging.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
default_logger.addHandler(fh)
try:
    import multiprocessing, tkinter as tk, time, webbrowser, os, signal, pickle, sys

    from tkinter.constants import *
    from tkinter.messagebox import showinfo, showerror, showwarning
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.scrolledtext import ScrolledText

    from platform_data_creator import PlatformDataCaptureWindow
    from screen_processor import MapleScreenCapturer
    from keystate_manager import DEFAULT_KEY_MAP
    from directinput_constants import keysym_map
    from macro_script import MacroController
    import authentication
except:
    default_logger.exception("error during import")

APP_TITLE = "MS-rbw"
VERSION = 1.0

def destroy_child_widgets(parent):
    for child in parent.winfo_children():
        child.destroy()

class SetKeyMap(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.wm_minsize(200, 30)
        self.master = master
        self.title("키설정")
        self.focus_get()
        self.grab_set()
        if not os.path.exists("keymap.keymap"):
            self.create_default_keymap()
        self.keymap_data = self.read_keymap_file()
        print(self.keymap_data)
        self.labels = {}
        keycount = 0
        _keyname = ""
        for keyname, value in self.keymap_data.items():
            dik_code, kor_name = value
            tk.Label(self, text=kor_name).grid(row=keycount, column=0)
            _keyname = keyname
            self.labels[_keyname] = tk.StringVar()
            self.labels[_keyname].set(self.dik2keysym(dik_code))
            tk.Button(self, textvariable=self.labels[_keyname], command=lambda _keyname=_keyname: self.set_key(_keyname)).grid(row=keycount, column=1)
            keycount += 1

        tk.Button(self, text="기본값 복원", command=self.set_default_keymap).grid(row=keycount, column=0)
        tk.Button(self, text="저장하고 종료", command=self.onSave).grid(row=keycount, column=1)

    def set_default_keymap(self):
        self.create_default_keymap()
        showinfo("키설정", "기본값으로 복원했습니다")
        self.destroy()

    def keysym2dik(self, keysym):
        try:
            dik = keysym_map[keysym]
            return dik
        except:
            return 0

    def onSave(self):
        with open("keymap.keymap", "wb") as f:
            pickle.dump({"keymap": self.keymap_data}, f)
        self.destroy()

    def onPress(self, event,  key_name):
        found = False
        for key, value in keysym_map.items():
            if event.keysym == key or str(event.keysym).upper() == key:
                self.keymap_data[key_name] = [value, self.keymap_data[key_name][1]]
                self.labels[key_name].set(key)
                found = True
                break
        if not found:
            showwarning("키설정", "현재 지원하지 않는 키입니다. 기본 키로 초기화 됩니다."+str(event.keysym))
            self.keymap_data[key_name] = DEFAULT_KEY_MAP[key_name]
            self.labels[key_name].set(self.dik2keysym(DEFAULT_KEY_MAP[key_name][0]))

        self.unbind("<Key>")

    def set_key(self, key_name):
        self.labels[key_name].set("키를 입력해 주세요")
        self.unbind("<Key>")
        self.bind("<Key>", lambda event: self.onPress(event, key_name))

    def dik2keysym(self, dik):
            for keysym, _dik in keysym_map.items():
                if dik == _dik:
                    return keysym


    def read_keymap_file(self):
        if os.path.exists("keymap.keymap"):
            with open("keymap.keymap", "rb") as f:
                try:
                    data = pickle.load(f)
                    keymap = data["keymap"]
                except:
                    return 0
                else:
                    return keymap

    def create_default_keymap(self):
        with open("keymap.keymap", "wb") as f:
            pickle.dump({"keymap": DEFAULT_KEY_MAP}, f)


def macro_loop(input_queue, output_queue):
    logger = logging.getLogger("macro_loop")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler("logging.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    try:
        while True:
            if not input_queue.empty():
                command = input_queue.get()
                logger.debug("recieved command {}".format(command))
                if command[0] == "start":
                    logger.debug("starting MacroController...")
                    keymap = command[1]
                    platform_file_dir = command[2]
                    macro = MacroController(keymap, log_queue=output_queue)
                    macro.load_and_process_platform_map(platform_file_dir)

                    while True:
                        macro.loop()
                        if not input_queue.empty():
                            command = input_queue.get()
                            if command[0] == "stop":
                                macro.abort()
                                break
    except:
        output_queue.put(["log", "!! 매크로 프로세스에서 오류가 발생했습니다. 로그파일을 확인해주세요. !!", ])
        output_queue.put(["exception", "exception"])
        logger.exception("Exeption during loop execution:")




class MainScreen(tk.Frame):
    def __init__(self, master, user_id="null", expiration_time=0):
        self.master = master
        destroy_child_widgets(self.master)
        tk.Frame.__init__(self, master)
        self.pack(expand=YES, fill=BOTH)
        self.user_id = user_id
        self.expiration_time = expiration_time

        self.menubar = tk.Menu()
        self.menubar.add_command(label="지형파일 생성하기", command=lambda: PlatformDataCaptureWindow())
        self.menubar.add_command(label="키 설정하기", command=lambda: SetKeyMap(self.master))

        self.master.config(menu=self.menubar)


        self.platform_file_dir = tk.StringVar()
        self.platform_file_name = tk.StringVar()

        self.keymap = None

        self.auth_info_frame = tk.Frame(self, borderwidth=2, relief=GROOVE)
        self.auth_info_frame.pack(side=TOP, anchor=NW)

        self.macro_pid = 0
        self.macro_process = None
        self.macro_process_out_queue = multiprocessing.Queue()
        self.macro_process_in_queue = multiprocessing.Queue()

        self.macro_pid_infotext = tk.StringVar()
        self.macro_pid_infotext.set("실행되지 않음")

        tk.Label(self.auth_info_frame, text="아이디: %s"%(self.user_id)).pack(side=TOP)
        tk.Label(self.auth_info_frame, text="만료시간: %s"%(time.strftime('%Y %m %d %H:%M:%S', time.localtime(self.expiration_time)))).pack(side=BOTTOM)

        self.log_text_area = ScrolledText(self, height = 10, width = 20)
        self.log_text_area.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self.log_text_area.bind("<Key>", lambda e: "break")
        self.macro_info_frame = tk.Frame(self, borderwidth=1, relief=GROOVE)
        self.macro_info_frame.pack(side=BOTTOM, anchor=S, expand=YES, fill=BOTH)

        tk.Label(self.macro_info_frame, text="매크로 프로세스 상태:").grid(row=0, column=0)

        self.macro_process_label = tk.Label(self.macro_info_frame, textvariable=self.macro_pid_infotext, fg="red")
        self.macro_process_label.grid(row=0, column=1, sticky=N+S+E+W)
        self.macro_process_toggle_button = tk.Button(self.macro_info_frame, text="실행하기", command=self.toggle_macro_process)
        self.macro_process_toggle_button.grid(row=0, column=2, sticky=N+S+E+W)

        tk.Label(self.macro_info_frame, text="지형 파일:").grid(row=1, column=0, sticky=N+S+E+W)
        tk.Label(self.macro_info_frame, textvariable=self.platform_file_name).grid(row=1, column=1, sticky=N+S+E+W)
        self.platform_file_button = tk.Button(self.macro_info_frame, text="파일 선택하기", command=self.onPlatformFileSelect)
        self.platform_file_button.grid(row=1, column=2, sticky=N+S+E+W)

        self.macro_start_button = tk.Button(self.macro_info_frame, text="매크로 시작", fg="green", command=self.start_macro)
        self.macro_start_button.grid(row=2, column=0, sticky=N+S+E+W)
        self.macro_end_button = tk.Button(self.macro_info_frame, text="매크로 종료", fg="red", command=self.stop_macro, state=DISABLED)
        self.macro_end_button.grid(row=2, column=1, sticky=N + S + E + W)



        for x in range(5):
            self.macro_info_frame.grid_columnconfigure(x, weight=1)
        self.log("MS-rbw", VERSION)
        self.log("해당 프로그램 사용시 발생하는 모든 제재사항 및 불이익은 사용자에게 있습니다")

        self.master.protocol("WM_DELETE_WINDOW", self.onClose)
        self.after(600000, self.check_license)
        self.after(500, self.toggle_macro_process)
        self.after(1000, self.check_input_queue)

    def check_input_queue(self):
        while not self.macro_process_in_queue.empty():
            output = self.macro_process_in_queue.get()
            if output[0] == "log":
                self.log("Process - "+str(output[1]))
            elif output[0] == "stopped":
                self.log("매크로가 완전히 종료되었습니다.")
            elif output[0] == "exception":
                self.macro_end_button.configure(state=DISABLED)
                self.macro_start_button.configure(state=NORMAL)
                self.platform_file_button.configure(state=NORMAL)
                self.macro_process = None
                self.macro_pid = 0
                self.macro_process_toggle_button.configure(state=NORMAL)
                self.macro_pid_infotext.set("실행되지 않음")
                self.macro_process_label.configure(fg="red")
                self.macro_process_toggle_button.configure(text="실행하기")
                self.log("오류로 인해 매크로 프로세스가 종료되었습니다.")

        self.after(1000, self.check_input_queue)

    def check_license(self):
        self.log("인증 확인중...")
        auth_result = authentication.authenticate_device()
        if auth_result[0] == 2:
            self.log("인증 확인완료")
            self.after(600000, self.check_license)
        else:
            self.log("인증 실패")
            showerror(APP_TITLE, "인증에 실패했습니다. 인증상태를 확인하고 다시 실행해주세요.")
            self.onClose()

    def onClose(self):
        if self.macro_process:
            try:
                self.macro_process_out_queue.put("stop")
                os.kill(self.macro_pid, signal.SIGTERM)
            except:
                pass

        sys.exit()

    def start_macro(self):
        if not self.macro_process:
            self.toggle_macro_process()
        keymap = self.get_keymap()
        if not keymap:
            showerror(APP_TITLE, "키설정을 읽어오지 못했습니다. 키를 다시 설정해주세요.")
        else:
            if not self.platform_file_dir.get():
                showwarning(APP_TITLE, "지형 파일을 선택해 주세요.")
            else:
                if not MapleScreenCapturer().ms_get_screen_hwnd():
                    showwarning(APP_TITLE, "메이플 창을 찾지 못했습니다. 메이플을 실행해 주세요")
                else:

                    cap = MapleScreenCapturer()
                    hwnd = cap.ms_get_screen_hwnd()
                    rect = cap.ms_get_screen_rect(hwnd)
                    self.log("MS hwnd", hwnd)
                    self.log("MS rect", rect)
                    self.log("Out Queue put:", self.platform_file_dir.get())
                    if rect[0] < 0 or rect[1] < 0:
                        showwarning(APP_TITLE, "메이플 창 위치를 가져오는데 실패했습니다.\n메이플 촹의 좌측 상단 코너가 화면 내에 있도록 메이플 창을 움직여주세요.")

                    else:
                        cap.capture()
                        self.macro_process_out_queue.put(("start", keymap, self.platform_file_dir.get()))
                        self.macro_start_button.configure(state=DISABLED)
                        self.macro_end_button.configure(state=NORMAL)
                        self.platform_file_button.configure(state=DISABLED)

    def stop_macro(self):
        self.macro_process_out_queue.put(("stop",))
        self.log("매크로 중지 요청 완료. 멈출때까지 잠시만 기다려주세요.")
        self.macro_end_button.configure(state=DISABLED)
        self.macro_start_button.configure(state=NORMAL)
        self.platform_file_button.configure(state=NORMAL)

    def get_keymap(self):
        if os.path.exists("keymap.keymap"):
            with open("keymap.keymap", "rb") as f:
                try:
                    data = pickle.load(f)
                    keymap = data["keymap"]
                except:
                    return 0
                else:
                    return keymap


    def log(self, *args):
        res_txt = []
        for arg in args:
            res_txt.append(str(arg))
        self.log_text_area.insert(END, " ".join(res_txt)+"\n")
        self.log_text_area.see(END)

    def toggle_macro_process(self):
        if not self.macro_process:
            self.macro_process_toggle_button.configure(state=DISABLED)
            self.macro_pid_infotext.set("실행중..")
            self.macro_process_label.configure(fg="orange")
            self.log("매크로 프로세스 시작중...")
            self.macro_process_out_queue = multiprocessing.Queue()
            self.macro_process_in_queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=macro_loop, args=(self.macro_process_out_queue, self.macro_process_in_queue))
            p.daemon = True

            self.macro_process = p
            p.start()
            self.macro_pid = p.pid
            self.log("프로세스 생성완료(pid: %d)"%(self.macro_pid))
            self.macro_pid_infotext.set("실행됨(%d)"%(self.macro_pid))
            self.macro_process_label.configure(fg="green")
            self.macro_process_toggle_button.configure(state=NORMAL)
            self.macro_process_toggle_button.configure(text="중지하기")

        else:
            self.stop_macro()
            self.macro_process_toggle_button.configure(state=DISABLED)
            self.macro_pid_infotext.set("중지중..")
            self.macro_process_label.configure(fg="orange")

            self.log("SIGTERM %d"%(self.macro_pid))
            os.kill(self.macro_pid, signal.SIGTERM)
            self.log("프로세스 종료완료")
            self.macro_process = None
            self.macro_pid = 0
            self.macro_process_toggle_button.configure(state=NORMAL)
            self.macro_pid_infotext.set("실행되지 않음")
            self.macro_process_label.configure(fg="red")
            self.macro_process_toggle_button.configure(text="실행하기")

    def onPlatformFileSelect(self):
        platform_file_path = askopenfilename(initialdir=os.getcwd(), title="지형파일 선택", filetypes=(("지형 파일(*.platform)", "*.platform"),))
        if platform_file_path:
            if os.path.exists(platform_file_path):
                with open(platform_file_path, "rb") as f:
                    try:
                        data = pickle.load(f)
                        platforms = data["platforms"]
                        oneway_platforms = data["oneway"]
                        minimap_coords = data["minimap"]
                        self.log("지형파일 로딩 완료(플랫폼 갯수: ", len(platforms.keys()), "일방 플랫폼 갯수:",
                                 len(oneway_platforms.keys()))
                    except:
                        showerror(APP_TITLE, "파일 검증 오류\n 파일: %s\n파일 검증에 실패했습니다. 깨진 파일인지 확인해주세요."%(platform_file_path))
                    else:
                        self.platform_file_dir.set(platform_file_path)
                        self.platform_file_name.set(platform_file_path.split("/")[-1])


class AuthScreen(tk.Frame):
    def __init__(self, master):
        self.master = master
        destroy_child_widgets(self.master)
        tk.Frame.__init__(self, master)
        self.pack(expand=YES, fill=BOTH)

        self.userid_input = tk.StringVar()
        self.userpass_input = tk.StringVar()
        auth_res = authentication.authenticate_device()
        if auth_res[0] == 0:
            tk.Label(self, text="PC 인증 안내").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text="사용기간이 만료되었습니다. 카톡으로 문의하여 기간연장을 신청하시기 바랍니다.").grid(row=1, column=0, columnspan=2)
            tk.Label(self, text="만료시간").grid(row=2, column=0)
            tk.Label(self, text=time.strftime('%Y %m %d %H:%M:%S', time.localtime(auth_res[3]))).grid(row=2, column=1)
            tk.Label(self, text="동록된 아이디").grid(row=3, column=0)
            tk.Label(self, text=auth_res[2]).grid(row=3, column=1)
            tk.Button(self, text="등록사이트 열기", command=lambda:webbrowser.open("http://ms-rbw.appspot.com")).grid(row=4, column=0, columnspan=2)
        elif auth_res[0] == 1:
            tk.Label(self, text="PC 인증 안내").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text="등록되지 않은 PC입니다. 구매자인 경우 PC등록을 진행해주시고, 비구매자인 경우 카카오톡으로 문의 바랍니다(등록사이트에 링크있음).").grid(row=1, column=0, columnspan=2)
            tk.Label(self, text="PC이름: %s"%(str(os.getenv("COMPUTERNAME")))).grid(row=2, column=0, columnspan=2)
            tk.Label(self, text="아이디").grid(row=3, column=0)
            tk.Entry(self, textvariable=self.userid_input).grid(row=3, column=1)
            tk.Label(self, text="비밀번호").grid(row=4, column=0)
            tk.Entry(self, textvariable=self.userpass_input, show="*").grid(row=4, column=1)
            tk.Button(self, text="등록사이트 열기", command=lambda: webbrowser.open("http://ms-rbw.appspot.com")).grid(row=5,column=0)
            tk.Button(self, text="로그인 및 기기등록", command=self.onDeviceAuthLogin).grid(row=5, column=1)
        elif auth_res[0] == 2:
            MainScreen(self.master, user_id=auth_res[2], expiration_time=auth_res[3])

        elif auth_res[0] == -1:
            tk.Label(self, text="PC 인증 안내").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text="PC인증 도중 오류가 발생했습니다. 카카오톡 문의 또는 등록사이트 확인 바랍니다.").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="등록사이트 열기", command=lambda: webbrowser.open("http://ms-rbw.appspot.com")).grid(row=2,column=0,columnspan=2)

    def onDeviceAuthLogin(self):
        if self.userpass_input.get() and self.userid_input.get():
            id = self.userid_input.get()
            password = self.userpass_input.get()
            self.userpass_input.set("")
            self.userid_input.set("")
            addpc_res = authentication.add_pc(id, password)

            if addpc_res[0] == 2:
                showinfo("인증 성공", "인증이 완료되었습니다. 프로그램을 다시 실행해주세요.")
                sys.exit()

            elif addpc_res[0] == 0:
                destroy_child_widgets(self)
                tk.Label(self, text="PC수 한도만큼 PC가 등록되어 PC등록에 실패했습니다.").grid(row=0, column=0)
                tk.Label(self, text="등록사이트에서 불필요 PC를 해제하거나, PC한도를 증가해야 합니다.").grid(row=1, column=0)
                tk.Label(self, text="현재 PC 수: %d대"%(addpc_res[1])).grid(row=2, column=0)
                tk.Button(self, text="등록사이트 열기", command=lambda: webbrowser.open("http://ms-rbw.appspot.com")).grid(row=3, column=0)

            elif addpc_res[0] == 1:
                showwarning("인증 오류", "아이디 혹은 비밀번호를 확인해주세요")

            elif addpc_res[0] == -1:
                showwarning("인증 오류", "등록중 오류가 발생했습니다. 카카오톡 문의 또는 등록사이트 확인 바랍니다.")
        else:
            showwarning("인증 오류", "아이디와 비밀번호를 입력해주세요")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    root.title(APP_TITLE)
    root.resizable(0,0)
    #CreatePlatformFileFrame(root)
    AuthScreen(root)
    root.mainloop()
