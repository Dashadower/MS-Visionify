from dinput_constants import *
import keyboard_input_handler as ki
import time
from windows_tools import set_maplestory_focus



def jump():
    ki.singlepress(DIK_ALT)

set_maplestory_focus()
time.sleep(1)
for x in range(2):
    ki.PressKey(DIK_RIGHT)
    ki.singlepress(DIK_ALT)
    time.sleep(0.2)
    ki.PressKey(DIK_ALT)
    time.sleep(2)
    ki.ReleaseKey(DIK_ALT)
    ki.ReleaseKey(DIK_RIGHT)
    time.sleep(1)
    ki.PressKey(DIK_LEFT)
    ki.singlepress(DIK_ALT)
    time.sleep(0.2)
    ki.PressKey(DIK_ALT)
    time.sleep(2)
    ki.ReleaseKey(DIK_ALT)
    ki.ReleaseKey(DIK_LEFT)
    time.sleep(2)
    ki.singlepress(DIK_A)
    time.sleep(1)
