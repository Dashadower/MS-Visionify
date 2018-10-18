import numpy as np
import cv2, imutils, os
from src.screen_processor import MapleScreenCapturer
from src.monster_detector import MonsterTemplateDetector
from src.player_medal_detector import PlayerMedalDetector
from src.screen_processor import StaticImageProcessor
from src.terrain_analyzer import PathAnalyzer

screencap = MapleScreenCapturer()
scrp = StaticImageProcessor(screencap)
scrp.update_image()
area = scrp.get_minimap_rect()
pathextractor = PathAnalyzer()

while True:
    scrp.update_image(set_focus=False)

    playerpos = scrp.find_player_minimap_marker(area)
    if playerpos != 0:
        print(playerpos)
        pathextractor.input(playerpos[0], playerpos[1])

    cropped_img = cv2.cvtColor(scrp.rgb_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]], cv2.COLOR_BGR2RGB)

    if pathextractor.platforms:
        for platform in pathextractor.platforms:
            cv2.line(cropped_img, platform[0], platform[1], (0, 255, 0), 2)

    if pathextractor.ladders:
        for ladder in pathextractor.ladders:
            cv2.line(cropped_img, ladder[0], ladder[1], (0, 0, 255), 2)
    cropped_img = imutils.resize(cropped_img, width=500)
    cv2.imshow("test", cropped_img)

    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()
        pathextractor.reset()

os.chdir("../src")
mobdetector = MonsterTemplateDetector("img/ArcaneRiver/ChewChew/츄츄 아일랜드.json")
playerdetector = PlayerMedalDetector()
mobdetector.create_template("mob1.png")
playerdetector.create_template("medal1.png")
print(pathextractor.platforms)
while True:
    scrp.update_image(set_focus=False)

    playercoord = scrp.find_player_minimap_marker(area)
    player_marker_pos = playerdetector.find(scrp.gray_img)
    cplatform = None
    if playercoord:
        for platform in pathextractor.platforms:
            if playercoord[0] >= platform[0][0] and playercoord[0] <= platform[1][0]:
                if playercoord[1] >= platform[0][1]-10 and playercoord[1] <= platform[0][1]+10:
                    print("found platform")
                    cplatform = platform
                    minbound_x = playercoord[0] - cplatform[0][0]
                    maxbound_x = cplatform[1][1] - playercoord[0]
    mobcount = 0
    if cplatform:
        roi_x_min = player_marker_pos[0]-(minbound_x*16)
        roi_x_max = player_marker_pos[0]+maxbound_x*16
        roi_y_min = player_marker_pos[1]-100
        roi_y_max = player_marker_pos[1]+10
        cropped_img = scrp.gray_img[roi_y_min:roi_y_max, roi_x_min:roi_x_max]
        cv2.imshow("", cropped_img)
        detected_monsters = mobdetector.find(cropped_img)
        for coord in detected_monsters:
            if coord[0] >= cplatform[0][0] and coord[0] <= cplatform[1][0]:
                if coord[1] >= cplatform[0][1]-10 and coord[1] <= cplatform[0][1]+10:
                    mobcount += 1
    print(mobcount)
