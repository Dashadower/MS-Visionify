from windows_tools import _get_maplestory_screen, get_maplestory_coords
import cv2, imutils, time
import numpy as np
from PIL import ImageGrab
from keyboard_input_handler import singlepress
from dinput_constants import numbers, DIK_RETURN, DIK_COMMA



player_pos = None

# constants for find_minimap_area
best_area = 0
default_minimap_roi = [0, 40, 400, 300]
detection_area = [0,40,400,300]

lower_player = np.array([60,220,250])
upper_player = np.array([70,230,255])

def find_minimap_area(original_image, best_rect_area = 0, debug = False):
    """Input: BGR image. Output: estimed bounding box(x,y,w,h) of minimap area"""
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.GaussianBlur(processed_img, (3, 3), 3)
    processed_img = cv2.erode(processed_img, (7,7))
    #processed_img = cv2.dilate(processed_img, (7,7))
    processed_img = cv2.Canny(processed_img, threshold1=180, threshold2=255)
    coords = None
    contourarea = 0
    im2, contours, hierarchy = cv2.findContours(processed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) >= best_rect_area and cv2.contourArea(c) >= 100 and cv2.contourArea(c) <= 30000:

            coords = cv2.boundingRect(c)
            if coords[0] > 0 and coords[1] > 0 and coords[2] > 0 and coords[2] > 0:
                pass
            else:
                coords = None
            contourarea = cv2.contourArea(c)

    if contourarea >= best_rect_area:
        pass
    else:
        coords = None
    if debug:
        return coords, contourarea, processed_img
    else:
        return coords, contourarea


def find_player_marker(img):
    mask = cv2.inRange(img, lower_player, upper_player)
    td = np.transpose(np.where(mask>0)).tolist()
    if len(td) > 0:
        avg_x = 0
        avg_y = 0
        totalpoints = 0
        for coord in td:
            avg_y += coord[0]
            avg_x += coord[1]
            totalpoints += 1
        avg_y = int(avg_y/totalpoints)
        avg_x = int(avg_x/totalpoints)
        return (avg_x, avg_y)
    else: return 0



def find_other_player_marker(img):
    mask = cv2.inRange(img, (0,0,255), (0,0,255))
    td = np.transpose(np.where(mask > 0)).tolist()
    if len(td) > 0:
        avg_x = 0
        avg_y = 0
        totalpoints = 0
        for coord in td:
            avg_y += coord[0]
            avg_x += coord[1]
            totalpoints += 1
        avg_y = int(avg_y/totalpoints)
        avg_x = int(avg_x/totalpoints)
        return (avg_x, avg_y)
    else: return 0



while True:

    captured_img = _get_maplestory_screen()
    if not captured_img:
        print("cant find maplestory")
        break
    screenshot = cv2.cvtColor(np.array(captured_img), cv2.COLOR_RGB2BGR)
    screenshot = screenshot[default_minimap_roi[1]:default_minimap_roi[3], default_minimap_roi[0]:default_minimap_roi[2]]
    minimap_coord = find_minimap_area(screenshot, best_area)[0]
    if minimap_coord:
        detection_area = [minimap_coord[0], minimap_coord[1], minimap_coord[0]+minimap_coord[2], minimap_coord[1]+minimap_coord[3]]
    minimap_area = screenshot[detection_area[1]:detection_area[3], detection_area[0]:detection_area[2]]
    pos = find_player_marker(minimap_area)
    if pos:
        print(pos)
    cv2.imshow("", minimap_area)




    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        print("reset_area")
        best_area = 0
        detection_area = default_minimap_roi
