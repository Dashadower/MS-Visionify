import directinput_constants as dic
import time, ctypes, threading
from win32api import GetKeyState
from win32con import VK_NUMLOCK

SendInput = ctypes.windll.user32.SendInput
# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actual Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))  # 0x0008: KEYEVENTF_SCANCODE
    x = Input( ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))  # 0x0002: KEYEVENTF_KEYUP


class KeyboardInputManager:
    """Manage keyboard input by using 2 states
    state 0: key is not pressed and up
    state 1: key is down and pressed"""
    def __init__(self, debug=False):
        """dict key_state : list of keycodes with either 0 or 1 as value. Indicates whether the use wants to change the value of keycodes
        dict actual_key_state: list of keycodes with states as value where the key is actually pressed.
         Differences between this dict and key_state can be used to determine whether the key should be pressed or released"""
        self.key_state = {}
        self.actual_key_state = {}
        self.debug = debug

    def get_key_state(self, key_code=None):
        if key_code:
            if key_code in self.key_state.keys():
                return self.key_state[key_code]
            else:
                return None
        else:
            return self.key_state

    def set_key_state(self, key_code, value):
        self.key_state[key_code] = value

    def translate_key_state(self):
        for keycode, state in self.key_state.items():
            if keycode in self.actual_key_state.keys():
                if self.actual_key_state[keycode] != state:
                    if state:
                        PressKey(keycode)
                        self.actual_key_state[keycode] = 1
                    elif not state:
                        ReleaseKey(keycode)
                        self.actual_key_state[keycode] = 0
            else:
                if state:
                    PressKey(keycode)
                    self.actual_key_state[keycode] = 1
                elif not state:
                    ReleaseKey(keycode)
                    self.actual_key_state[keycode] = 0

    def _direct_press(self, key_code):
        PressKey(key_code)
        self.actual_key_state[key_code] = 1

    def _direct_release(self, key_code):
        ReleaseKey(key_code)
        self.actual_key_state[key_code] = 0

    def reset(self):
        self.key_state = {}
        self.translate_key_state()

class AdvancedThreadedKeyboardHandler(KeyboardInputManager):
    def __init__(self, tickrate=0.01):
        super().__init__()
        pass

