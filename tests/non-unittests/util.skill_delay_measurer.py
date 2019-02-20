import cv2, imutils, os
from src.screen_processor import MapleScreenCapturer
from src.screen_processor import StaticImageProcessor
from src.keystate_manager import KeyboardInputManager
import src.directinput_constants
import numpy as np, time

screencap = MapleScreenCapturer()
scrp = StaticImageProcessor(screencap)
scrp.update_image()
area = scrp.get_minimap_rect()
key_mgr = KeyboardInputManager()

testkey = src.directinput_constants.DIK_A

while True:
    scrp.update_image(set_focus=False)
    minimap_image = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]
    playerpos = scrp.find_player_minimap_marker(area)
    if playerpos:
        cv2.circle(minimap_image, playerpos, 4, (255, 0, 0), -1)
    regular_find = imutils.resize(minimap_image, width=400)
    cv2.imshow("s to start measuring", regular_find)

    #print("regular", playerpos)
    #print("templ", playerpos_templ)

    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        break

    elif inp == ord("r"):
        scrp.reset_minimap_area()
        scrp.update_image(set_focus=False)
        area = scrp.get_minimap_rect()

    elif inp == ord("s"):
        time.sleep(2)
        key_mgr.single_press(testkey)
        s = time.time()
        key_mgr._direct_press(src.directinput_constants.DIK_RIGHT)
        last_coords = playerpos
        while True:
            scrp.update_image()
            cpos = scrp.find_player_minimap_marker(area)
            if last_coords != cpos:
                print(time.time() - s)
                key_mgr._direct_release(src.directinput_constants.DIK_RIGHT)
                break
            else:
                print(last_coords, cpos)