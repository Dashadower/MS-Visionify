from src.screen_processor import MapleScreenCapturer
import cv2, imutils, os
from src.monster_detector import MonsterTemplateDetector
from src.player_medal_detector import PlayerMedalDetector
import numpy as np
os.chdir("../src")
wincap = MapleScreenCapturer()
detector = MonsterTemplateDetector("img/ArcaneRiver/ChewChew/츄츄 아일랜드.json")
playerdetector = PlayerMedalDetector()
detector.create_template("mob1.png")
playerdetector.create_template("medal1.png")
capture_width = 700
capture_height = 200
while True:
    img = wincap.capture(set_focus=False)
    grayscale = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    playerloc = playerdetector.find(grayscale)
    detected = []
    if playerloc:
        bbox = grayscale[max((playerloc[1] - int(capture_height / 2)), 0):max((playerloc[1] + int(capture_height / 2)), 0),
               (playerloc[0] - int(capture_width / 2)):(playerloc[0] + int(capture_width / 2))]
        cv2.rectangle(grayscale, (playerloc[0] - int(capture_width / 2), playerloc[1] - int(capture_height / 2)), (playerloc[0] + int(capture_width / 2), playerloc[1] + int(capture_height / 2)),(0,0,255), 3)
        detected = detector.find(grayscale)
        cv2.circle(grayscale, playerloc, 15, (0,0,255), -1)

    if detected:
        for point in detected:
            cv2.circle(grayscale, (playerloc[0] - int(capture_width / 2)+point[0], playerloc[1] - int(capture_height / 2)+point[1]), 20, (0,0,255), -1)

    cv2.imshow("", imutils.resize(grayscale, width=500))
    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
