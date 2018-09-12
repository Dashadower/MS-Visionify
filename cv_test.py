from windows_tools import set_window_focus, get_maplestory_window_hwnd, isAdmin
import time
from keyboard_input_handler import PressKey, ReleaseKey, singlepress, DIK_ALT, DIK_LEFT, DIK_NUMLOCK, get_numlock_status, DIK_A, DIK_Q, DIK_RMENU, DIK_RETURN


assert isAdmin(), "Admin privillages are needed to run win32api tools."

if get_numlock_status():
    singlepress(DIK_NUMLOCK)
    pass

set_window_focus(get_maplestory_window_hwnd())

time.sleep(2)
print("start")

PressKey(DIK_ALT)

