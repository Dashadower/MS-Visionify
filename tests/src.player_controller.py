from src.player_controller import PlayerController
from src.keystate_manager import KeyboardInputManager
import time
from src.screen_processor import MapleScreenCapturer
from src.screen_processor import StaticImageProcessor
from win32gui import SetForegroundWindow

wcap = MapleScreenCapturer()
scrp = StaticImageProcessor(wcap)
hwnd = wcap.ms_get_screen_hwnd()
kbd_mgr = KeyboardInputManager()
player_cntrlr = PlayerController(kbd_mgr, scrp)

SetForegroundWindow(hwnd)
time.sleep(0.5)
player_cntrlr.update()
print(player_cntrlr.x, player_cntrlr.y)
player_cntrlr.optimized_horizontal_move(player_cntrlr.x + 20)
player_cntrlr.update()
print(player_cntrlr.x, player_cntrlr.y)

