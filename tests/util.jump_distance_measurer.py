import cv2, imutils, os
from src.screen_processor import MapleScreenCapturer
from src.screen_processor import StaticImageProcessor
from matplotlib import pyplot as plt
import numpy as np

screencap = MapleScreenCapturer()
scrp = StaticImageProcessor(screencap)
scrp.update_image()
area = scrp.get_minimap_rect()
print(area)
os.chdir("../src")


jmp_coords = []
start_x = None
start_y = None
end_x = None
end_y = None
last_coords = None
is_recording = False
min_y = 10000


while True:
    scrp.update_image(set_focus=False)

    playerpos = scrp.find_player_minimap_marker(area) # use minimap
    #playerpos = medal.find(scrp.gray_img) # use screen medal
    if playerpos:
        if playerpos != last_coords:
            print(playerpos)
            if is_recording:
                jmp_coords.append(playerpos)
                min_y = min(min_y, playerpos[1])
            last_coords = playerpos
    cv2.imshow("a to record",imutils.resize(scrp.bgr_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]], width=400))
    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("a"):
        if not is_recording:
            start_x = playerpos[0]
            start_y = playerpos[1]
            is_recording = True

            print("recording started")
            jmp_coords.append(playerpos)
        elif is_recording:
            end_x = playerpos[0]
            end_y = playerpos[1]

            is_recording = False

            starttime = 0
            endtime = 0
            print("finished")
            print(jmp_coords)
            print("y coord movement:", abs(start_y - min_y))
            print("x coord movement:", abs(start_x - end_x))

    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()



start_x = 91
start_y = 34
end_x = 101
_jmp_coords = []
for obj in jmp_coords:
    _jmp_coords.append((obj[0], -obj[1]))
x_val = [x[0] for x in _jmp_coords]
y_val = [y[1] for y in _jmp_coords]
#x = np.linspace(start_x, end_x, 500)
#y = (0.53*(x-((start_x+end_x)/2)))**2 + start_y - 7.3
plt.scatter(x_val, y_val)
plt.gca().set_aspect('equal', adjustable='box')
#plt.plot(x, y)
plt.show()
