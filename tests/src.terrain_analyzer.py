from src.screen_processor import StaticImageProcessor, MapleScreenCapturer
from src.terrain_analyzer import PathAnalyzer
import cv2, imutils

wincap = MapleScreenCapturer()
scrp = StaticImageProcessor(wincap)
scrp.update_image()
area = scrp.get_minimap_rect()
pathextractor = PathAnalyzer()


while True:
    scrp.update_image(set_focus=False)
    #print("minimap area", area)

    if not area == 0:

        playerpos = scrp.find_player_minimap_marker(area)
        if playerpos != 0:
            pathextractor.input(playerpos[0], playerpos[1])


        cropped_img = cv2.cvtColor(scrp.rgb_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]], cv2.COLOR_BGR2RGB)

        if pathextractor.platforms:
            for platform in pathextractor.platforms:
                cv2.line(cropped_img,platform[0], platform[1],(0,255,0), 2)

        if pathextractor.ladders:
            for ladder in pathextractor.ladders:
                cv2.line(cropped_img, ladder[0], ladder[1], (0,0,255), 2)
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