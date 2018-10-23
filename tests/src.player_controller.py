from src.player_controller import PlayerController
from src.keystate_manager import KeyboardInputManager
import time
from src.screen_processor import MapleScreenCapturer
from win32gui import SetForegroundWindow

wcap = MapleScreenCapturer()
hwnd = wcap.ms_get_screen_hwnd()
kbd_mgr = KeyboardInputManager()
player_cntrlr = PlayerController(kbd_mgr)

SetForegroundWindow(hwnd)
time.sleep(0.5)
player_cntrlr.dbljump_max()

