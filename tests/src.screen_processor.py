import imutils, cv2, numpy as np, time
from src.screen_processor import MapleScreenCapturer
from src.screen_processor import StaticImageProcessor


screencap = MapleScreenCapturer()
scrp = StaticImageProcessor(screencap)
scrp.update_image()
area = scrp.get_minimap_rect()


while True:
    scrp.update_image(set_focus=False)
    st = time.time()
    playerpos = scrp.find_player_minimap_marker(area)
    et = time.time()
    print("regular", et - st)

    regular_find = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]].copy()
    if playerpos:
        cv2.circle(regular_find, playerpos, 4, (255, 0, 0), -1)
    regular_find = imutils.resize(regular_find, width=400)
    cv2.imshow("regular vs templ", regular_find)

    #print("regular", playerpos)
    #print("templ", playerpos_templ)

    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        break

    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()