import cv2, imutils, os
from src.screen_processor import MapleScreenCapturer
from src.screen_processor import StaticImageProcessor


screencap = MapleScreenCapturer()
scrp = StaticImageProcessor(screencap)
scrp.update_image()
area = scrp.get_minimap_rect()


miny = 10000
maxy = 0
while True:
    scrp.update_image(set_focus=False)

    playerpos = scrp.find_player_minimap_marker(area)
    """if playerpos != 0:
        miny = min(miny, playerpos[1])
        maxy = max(maxy, playerpos[1])

    print(miny, maxy)"""
    print(playerpos)
    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()