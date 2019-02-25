import tkinter as tk
from tkinter.constants import *
from tkinter.messagebox import showinfo, showwarning
import os, pickle
from directinput_constants import keysym_map
from keystate_manager import DEFAULT_KEY_MAP
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
        self.labels = {}
        keycount = 0
        _keyname = ""
        self.columnconfigure(1, weight=1, minsize=150)
        self.columnconfigure(0, weight=1)
        for keyname, value in self.keymap_data.items():
            dik_code, kor_name = value
            tk.Label(self, text=kor_name, borderwidth=1, relief=SOLID, padx=2).grid(row=keycount, column=0, sticky=N+S+E+W, pady=5, padx=(5,0))
            _keyname = keyname
            self.labels[_keyname] = tk.StringVar()
            self.labels[_keyname].set(self.dik2keysym(dik_code))
            tk.Button(self, textvariable=self.labels[_keyname], command=lambda _keyname=_keyname: self.set_key(_keyname), borderwidth=1, relief=SOLID).grid(row=keycount, column=1, sticky=N+S+E+W, pady=5, padx=(0,5))
            self.rowconfigure(keycount, weight=1)

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