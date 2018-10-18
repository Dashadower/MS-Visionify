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
while True:
    img = wincap.capture(set_focus=False)
    grayscale = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    detected = detector.find(grayscale)
    playerloc = playerdetector.find(grayscale)

    cv2.circle(grayscale, playerloc, 20, (0,0,255), -1)
    for point in detected:
        cv2.circle(grayscale, point, 20, (0,0,255), -1)

    cv2.imshow("", imutils.resize(grayscale, width=500))
    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
