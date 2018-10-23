from src.player_controller import PlayerController
from src.keystate_manager import KeyboardInputManager
import time

kbd_mgr = KeyboardInputManager()
player_cntrlr = PlayerController(kbd_mgr)

time.sleep(2)
player_cntrlr.jumpl()

