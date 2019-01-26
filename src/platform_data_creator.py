# -*- coding:utf-8 -*-
from screen_processor import StaticImageProcessor, MapleScreenCapturer
from terrain_analyzer import PathAnalyzer
import cv2, imutils, logging

def create_platform_file(file_name):
    default_logger = logging.getLogger("platform_file_creator")
    default_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler("logging.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    default_logger.addHandler(fh)

    try:
        wincap = MapleScreenCapturer()
        scrp = StaticImageProcessor(wincap)
        scrp.update_image(set_focus=False)
        area = scrp.get_minimap_rect()
        pathextractor = PathAnalyzer()
        input_mode = 1
        while True:
            scrp.update_image(set_focus=False)
            print("R2")
            if not area == 0:
                playerpos = scrp.find_player_minimap_marker(area)

                if playerpos != 0:
                    if input_mode == 1:
                        pathextractor.input(playerpos[0], playerpos[1])
                    else:
                        pathextractor.input_oneway_platform(playerpos[0], playerpos[1])

                cropped_img = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]
                if playerpos != 0:
                    cv2.circle(cropped_img, playerpos, 3, (0, 0, 255), -1)
                if pathextractor.platforms or pathextractor.oneway_platforms:
                    for key, platform in pathextractor.platforms.items():
                        cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(0,255,0), 1)
                    for key, platform in pathextractor.oneway_platforms.items():
                        cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(255,0,0), 1)

                cropped_img = imutils.resize(cropped_img, width=500)

                cv2.imshow("pdc-screencap",cropped_img)

            inp = cv2.waitKey(1)


            if inp == ord('q'):
                cv2.destroyWindow("pdc-screencap")
                break
            elif inp == ord("r"):
                scrp.reset_minimap_area()
                area = scrp.get_minimap_rect()
                pathextractor.reset()

            elif inp == ord("o"):
                input_mode *= -1

            elif inp == ord("s"):
                pathextractor.save(file_name, area)
                break
    except:
        default_logger.exception("exception if platform data creator")

