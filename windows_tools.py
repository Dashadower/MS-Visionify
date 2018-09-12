import win32gui, time, ctypes, os

from PIL import ImageGrab
def get_maplestory_window_hwnd():
    hwnd = win32gui.FindWindow(0, "MapleStory")
    return hwnd

def set_window_focus(hwnd):
    win32gui.SetForegroundWindow(hwnd)

def get_maplestory_screen():
    hwnd = get_maplestory_window_hwnd()
    if not hwnd:
        return 0
    set_window_focus(hwnd)
    time.sleep(0.2)
    windowpos = win32gui.GetWindowRect(hwnd)
    #windowpos[1] += 40

    scrt = ImageGrab.grab(windowpos)
    return scrt

def get_maplestory_coords():
    hwnd = get_maplestory_window_hwnd()
    if not hwnd:
        return 0
    windowpos = win32gui.GetWindowRect(hwnd)
    return windowpos

def _get_maplestory_screen():
    hwnd = get_maplestory_window_hwnd()
    if not hwnd:
        return 0
    windowpos = win32gui.GetWindowRect(hwnd)
    # windowpos[1] += 40
    scrt = ImageGrab.grab(windowpos)
    return scrt

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin