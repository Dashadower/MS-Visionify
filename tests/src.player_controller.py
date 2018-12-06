from src.player_controller import PlayerController
from src.keystate_manager import KeyboardInputManager
import time
from src.screen_processor import MapleScreenCapturer, StaticImageProcessor
from win32gui import SetForegroundWindow

wcap = MapleScreenCapturer()
hwnd = wcap.ms_get_screen_hwnd()
kbd_mgr = KeyboardInputManager()
scrp = StaticImageProcessor(wcap)
pctlr = PlayerController(kbd_mgr, scrp)


SetForegroundWindow(hwnd)
time.sleep(0.5)
scrp.update_image()
area = scrp.get_minimap_rect()
px, py = scrp.find_player_minimap_marker(area)
print("cpos", px, py)
goal = px - 45
print("goal", goal)
pctlr.update(px, py)
pctlr.optimized_horizontal_move(goal)
scrp.update_image()
px, py = scrp.find_player_minimap_marker(area)
print("immediate endpos", px, py)
pctlr.update(px, py)
time.sleep(2)
scrp.update_image()
px, py = scrp.find_player_minimap_marker(area)
print("sleep endpos", px, py)
pctlr.update(px, py)

