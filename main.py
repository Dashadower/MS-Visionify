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




def process_mainscreen(img):
    processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.GaussianBlur(processed_img, (7,7), 3)
    processed_img = cv2.erode(processed_img, (7,7))
    processed_img = cv2.dilate(processed_img, (7, 7))
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=255)

    processed_img = imutils.resize(processed_img, width = 400)
    return processed_img

fgbg = cv2.createBackgroundSubtractorMOG2(history=1)

def background_subtraction(bgr_img):
    blurred = cv2.GaussianBlur(bgr_img, (3,3), 1)
    fgmask = fgbg.apply(blurred)
    fgmask = cv2.erode(fgmask, (13,13))
    fgmask = cv2.dilate(fgmask, (13,13))
    im2, contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    coords = []
    if contours:
        for c in contours:
            area = cv2.contourArea(c)
            if area >= 2000 and area <= 15000:
                coords.append(cv2.boundingRect(c))
    if len(coords) <= 8:
        return coords
    else:
        return None

def match_medal(src_gray_img, template):
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(src_gray_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return (top_left[0], top_left[1], bottom_right[0], bottom_right[1])



# 대박엔터 공동대표 칭호를 이용해 플레이어 위치 계산
medal_template = cv2.imread("player_pattern.png",0)

# 칭호-플레이어간 위치 차 계산(픽셀)
medal_player_x_offset = 60
medal_player_y_offset = -40

windowinfo = get_maplestory_coords()
screenwidth = windowinfo[3]-windowinfo[1]
mob_detection_height = 80
while True:

    captured_img = _get_maplestory_screen()
    if not captured_img:
        break
    screenshot = cv2.cvtColor(np.array(captured_img), cv2.COLOR_RGB2BGR)
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    player_pos = match_medal(screenshot_gray, medal_template)
    center = (int((player_pos[0]+player_pos[2])/2 + medal_player_x_offset), int((player_pos[1]+player_pos[3])/2 + medal_player_y_offset))
    cv2.circle(screenshot,center ,5,(0,255,0), -1)

    

    cv2.imshow("mainscreen", screenshot)

    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break

