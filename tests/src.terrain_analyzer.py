from src.screen_processor import StaticImageProcessor, MapleScreenCapturer
from src.terrain_analyzer import PathAnalyzer
import cv2, imutils

wincap = MapleScreenCapturer()
scrp = StaticImageProcessor(wincap)
scrp.update_image()
area = scrp.get_minimap_rect()
pathextractor = PathAnalyzer()
print(area)
while True:
    scrp.update_image(set_focus=False)
    #print("minimap area", area)

    if not area == 0:

        playerpos = scrp.find_player_minimap_marker(area)
        if playerpos != 0:
            pathextractor.input(playerpos[0], playerpos[1])

        print(pathextractor.platforms.items())
        cropped_img = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]

        if pathextractor.platforms:
            for key, platform in pathextractor.platforms.items():
                cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(0,255,0), 2)

        cropped_img = imutils.resize(cropped_img, width=500)

        cv2.imshow("test",cropped_img)

    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()
        pathextractor.reset()