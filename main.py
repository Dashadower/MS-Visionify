from windows_tools import _get_maplestory_screen
import cv2, imutils
import numpy as np
from PIL import ImageGrab




player_pos = None

# constants for find_minimap_area
best_area = 0
default_minimap_roi = [0, 40, 400, 300]
detection_area = [0,40,400,300]

lower_player = np.array([60,220,250])
upper_player = np.array([70,230,255])

def find_minimap_area(original_image):
    """Input: BGR image. Output: estimed bounding box(x,y,w,h) of minimap area"""
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.GaussianBlur(processed_img, (3, 3), 3)
    processed_img = cv2.dilate(processed_img, (7,7))
    processed_img = cv2.Canny(processed_img, threshold1=180, threshold2=255)

    im2, contours, hierarchy = cv2.findContours(processed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        global best_area, detection_area
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) >= best_area and cv2.contourArea(c) >= 100 and cv2.contourArea(c) <= 30000:

            detection_area = cv2.boundingRect(c)
            if detection_area[0] > 0 and detection_area[1] > 0 and detection_area[2] > 0 and detection_area[2] > 0:
                pass
            else:
                detection_area = default_minimap_roi
            best_area = cv2.contourArea(c)

    return processed_img


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



def process_mainscreen(img):
    processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.GaussianBlur(processed_img, (7,7), 3)
    processed_img = cv2.dilate(processed_img, (7, 7))
    #processed_img = cv2.erode(processed_img, (5,5))
    #processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=255)

    processed_img = imutils.resize(processed_img, width = 400)
    return processed_img


while True:

    captured_img = _get_maplestory_screen()
    if not captured_img:
        break
    img = cv2.cvtColor(np.array(captured_img), cv2.COLOR_RGB2BGR)
    minimap_roi_img = img.copy()[default_minimap_roi[1]:default_minimap_roi[3], default_minimap_roi[0]:default_minimap_roi[2]]
    processed_minimap_img = find_minimap_area(minimap_roi_img)
    minimap_img = minimap_roi_img.copy()
    minimap_img = minimap_img[detection_area[1]:detection_area[1]+detection_area[3], detection_area[0]:detection_area[0]+detection_area[2]]
    cv2.rectangle(minimap_roi_img, (detection_area[0], detection_area[1]), (detection_area[0]+detection_area[2], detection_area[1]+detection_area[3]),(0,255,0), 3)
    player_marker = find_player_marker(minimap_img)
    if player_marker:
        cv2.circle(minimap_img, player_marker, 5, (255,255,255), -1)
    #cv2.imshow("processed", processed_minimap_img)
    cv2.imshow("scanned window", minimap_roi_img)
    cv2.imshow("minimap", minimap_img)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break