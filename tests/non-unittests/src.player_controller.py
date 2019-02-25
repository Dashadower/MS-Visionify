from src.player_controller import PlayerController
from src.keystate_manager import KeyboardInputManager
import time
from src.screen_processor import MapleScreenCapturer
from src.screen_processor import StaticImageProcessor
import directinput_constants
from win32gui import SetForegroundWindow

wcap = MapleScreenCapturer()
scrp = StaticImageProcessor(wcap)
hwnd = wcap.ms_get_screen_hwnd()
kbd_mgr = KeyboardInputManager()
player_cntrlr = PlayerController(kbd_mgr, scrp)

SetForegroundWindow(hwnd)
time.sleep(0.5)
scrp.update_image()
print(scrp.get_minimap_rect())
print(scrp.find_player_minimap_marker())
player_cntrlr.update()

print(player_cntrlr.x, player_cntrlr.y)

#player_cntrlr.moonlight_slash_sweep_move(player_cntrlr.x + 100)
#player_cntrlr.optimized_horizontal_move(player_cntrlr.x + 1)
player_cntrlr.dbljump_timed(1)
#player_cntrlr.jumpr_glide()
#player_cntrlr.dbljump_half()
print(player_cntrlr.x, player_cntrlr.y)

