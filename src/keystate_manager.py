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
    """
    This is an attempt to manage input from a single source. It remembers key "states" , which consists of keypress
    modifications, and actuates them in a single batch.
    """
    def __init__(self, debug=False):
        """
        Class variables:
        self.key_state: Temporary state dictionary before being actuated. Dictionary with DIK key names as keys with
        0 or 1 as keys (0 for release, 1 for press)
        self.actual_key_state: Actual key state dictionary. This dictionary is used to keep track of which keys are
        currently being pressed. Same format as self.key_state
        :param debug: Debug flag
        """
        self.key_state = {}
        self.actual_key_state = {}
        self.debug = debug

    def get_key_state(self, key_code=None):
        """
        Returns key state or states of current manager state
        :param key_code : DIK key name of key to look up. Please refer to directinput_constants.py. If undefined, returns enture key state
        :return: None"""
        if key_code:
            if key_code in self.key_state.keys():
                return self.key_state[key_code]
            else:
                return None
        else:
            return self.key_state

    def set_key_state(self, key_code, value):
        """
        Explicitly sets key state for key_code by value
        :param key_code: DIK Key name of keycode
        :param value: 0 for released, 1 for pressed
        :return: None"""
        self.key_state[key_code] = value

    def single_press(self, key_code, duration=0.08):
        """
        Presses key_code for duration seconds. Since it uses time.sleep(), it is a blocking call.
        :param key_code: DIK key code of key
        :param duration: Float of keypress duration in seconds
        :return: None
        """
        self._direct_press(key_code)
        time.sleep(duration)
        self._direct_release(key_code)

    def translate_key_state(self):
        """
        Acuates key presses in self.key_state to self.actual_key_state by pressing keys and storing state in self.actual_key_state
        self.actual_key_state becomes self.key_state, and self.key_state will get reset
        :return: None
        """
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

        self.key_state = {}

    def _direct_press(self, key_code):
        PressKey(key_code)
        #self.actual_key_state[key_code] = 1

    def _direct_release(self, key_code):
        ReleaseKey(key_code)
        #self.actual_key_state[key_code] = 0

    def reset(self):
        """
        Safe way of releasing all keys and resetting all states.
        :return: None
        """
        for keycode, state in self.key_state.items():
            if keycode in self.actual_key_state.keys():
                self.key_state[keycode] = 0
        self.translate_key_state()

DEFAULT_KEY_MAP = {
    "jump": dic.DIK_ALT,
    "moonlight_slash": dic.DIK_A,
    "thousand_sword": dic.DIK_F,
    "release_overload": dic.DIK_Q,
    "demon_strike": dic.DIK_1
}

class AdvancedThreadedKeyboardHandler(KeyboardInputManager):
    def __init__(self, tickrate=0.01):
        super().__init__()
        pass

