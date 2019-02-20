from src.screen_processor import StaticImageProcessor, MapleScreenCapturer
from src.terrain_analyzer import PathAnalyzer
import cv2, imutils

wincap = MapleScreenCapturer()
scrp = StaticImageProcessor(wincap)
scrp.update_image()
area = scrp.get_minimap_rect()
pathextractor = PathAnalyzer()
print(area)
input_mode = 1
while True:
    scrp.update_image(set_focus=False)
    #print("minimap area", area)

    if not area == 0:

        playerpos = scrp.find_player_minimap_marker(area)

        if playerpos != 0:
            if input_mode == 1:
                pathextractor.input(playerpos[0], playerpos[1])
            else:

                pathextractor.input_oneway_platform(playerpos[0], playerpos[1])


        print(pathextractor.platforms)
        #print(pathextractor.current_platform_coords)

        cropped_img = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]
        if playerpos != 0:
            cv2.circle(cropped_img, playerpos, 3, (0, 0, 255), -1)
        if pathextractor.platforms or pathextractor.oneway_platforms:
            for key, platform in pathextractor.platforms.items():
                cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(0,255,0), 2)
            for key, platform in pathextractor.oneway_platforms.items():
                print("oneway",key)
                cv2.line(cropped_img,(platform.start_x, platform.start_y), (platform.end_x, platform.end_y),(255,0,0), 2)

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

    elif inp == ord("o"):
        print("toggle mode")
        input_mode *= -1

    elif inp == ord("s"):
        filename = input("file name(with extension)?")
        pathextractor.save(filename+".platform", area)