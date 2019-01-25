# -*- coding:utf-8 -*-
#import macro_script
import multiprocessing, tkinter as tk, time, webbrowser, os
from tkinter.constants import *
from tkinter.messagebox import showinfo, showerror, showwarning
from platform_data_creator import create_platform_file
from authentication import authenticate_device

def destroy_child_widgets(parent):
    for child in parent.winfo_children():
        child.destroy()

class CreatePlatformFileFrame(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.wm_minsize(200, 30)
        self.master = master
        self.title("데이터파일 생성기")
        self.file_name = tk.StringVar()
        tk.Label(self, text="맵 지형 데이터파일 생성 툴").grid(row=0, column=0, columnspan=2)
        tk.Label(self, text="파일 이름:").grid(row=1, column=0)
        tk.Entry(self, textvariable=self.file_name).grid(row=1, column=1)
        tk.Button(self, text="생성툴 실행하기", command=self.onLaunch).grid(row=2, column=0, columnspan=2)

    def onLaunch(self):
        if not self.file_name.get():
            showwarning("데이터파일 생성기", "파일 이름을 입력해주세요")
        else:
            map_creator_process = multiprocessing.Process(target=create_platform_file, args=(self.file_name.get(),))
            map_creator_process.daemon = True
            map_creator_process.start()

class MainScreen(tk.Frame):
    def __init__(self, master, user_id=None, expiration_time=None):
        self.master = master
        destroy_child_widgets(self.master)
        tk.Frame.__init__(self, master)

        self.pack(expand=YES, fill=BOTH)


class AuthScreen(tk.Frame):
    def __init__(self, master):
        self.master = master
        destroy_child_widgets(self.master)
        tk.Frame.__init__(self, master)
        self.pack(expand=YES, fill=BOTH)
        auth_res = authenticate_device()
        if auth_res == 0:
            tk.Label(self, text="PC 인증 안내").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text="사용기간이 만료되었습니다. 카톡으로 문의하여 기간연장을 신청하시기 바랍니다.").grid(row=1, column=0, columnspan=2)
            tk.Label(self, text="만료시간:").grid(row=2, column=0)
            tk.Label(self, text=time.strftime('%Y %m %d %H:%M:%S', time.localtime(auth_res[3]))).grid(row=2, column=1)
            tk.Label(self, "동록된 아이디").grid(row=3, column=0)
            tk.Label(self, text=auth_res[2]).grid(row=3, column=1)
            tk.Button(self, text="등록사이트 열기", command=lambda:webbrowser.open("http://ms-rbw.appspot.com")).grid(row=4, column=0, columnspan=2)
        elif auth_res == 1:
            tk.Label(self, text="PC 인증 안내").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text="등록되지 않은 PC입니다. 구매자인 경우 PC등록을 진행해주시고, 비구매자인 경우 카카오톡으로 문의 바랍니다(등록사이트에 링크있음).").grid(row=1, column=0, columnspan=2)
            tk.Label(self, text="PC이름: %s"%(str(os.getenv("COMPUTERNAME")))).grid(row=2, column=0, columnspan=2)
            tk.Button(self, text="등록사이트 열기", command=lambda: webbrowser.open("http://ms-rbw.appspot.com")).grid(row=23,
                                                                                                                column=0,
                                                                                                                columnspan=2)
        elif auth_res == 2:
            MainScreen(self.master)

        elif auth_res == -1:
            tk.Label(self, text="PC 인증 안내").grid(row=0, column=0, columnspan=2)
            tk.Label(self, text="PC인증 도중 오류가 발생했습니다. 카카오톡 문의 또는 등록사이트 확인 바랍니다.").grid(row=1, column=0, columnspan=2)
            tk.Button(self, text="등록사이트 열기", command=lambda: webbrowser.open("http://ms-rbw.appspot.com")).grid(row=2,
                                                                                                                column=0,
                                                                                                                columnspan=2)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("MS-rbw")
    #CreatePlatformFileFrame(root)
    AuthScreen(root)
    root.mainloop()
