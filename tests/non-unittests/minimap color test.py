from src.screen_processor import MapleScreenCapturer, StaticImageProcessor
import cv2, numpy as np
mcap = MapleScreenCapturer()

scrp = StaticImageProcessor(mcap)
player_marker = np.array([68, 221, 255])
scrp.update_image()
area = scrp.get_minimap_rect()
print(area)
while True:
    scrp.update_image(set_focus=False)
    cropped = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]

    mask = cv2.inRange(cropped, player_marker, player_marker)
    td = np.transpose(np.where(mask > 0)).tolist()
    print(len(td))
    """if len(td) > 0:
        avg_x = 0
        avg_y = 0
        totalpoints = 0
        for coord in td:
            avg_y += coord[0]
            avg_x += coord[1]
            totalpoints += 1
        avg_y = int(avg_y / totalpoints)
        avg_x = int(avg_x / totalpoints)
        return avg_x, avg_y"""
    cv2.imshow("", mask)
    dt = cv2.waitKey(1)
    if dt == ord("q"):
        cv2.destroyAllWindows()
        break