import cv2, imutils, win32gui, time
from PIL import ImageGrab
import numpy as np

class MapleWindowNotFoundError(Exception):
    pass


MAPLESTORY_WINDOW_TITLE = "MapleStory"





class MapleScreenCapturer:
    """Container for capturing MS screen"""
    def __init__(self):
        pass

    def ms_get_screen_hwnd(self):
        window_hwnd = win32gui.FindWindow(0, MAPLESTORY_WINDOW_TITLE)
        if not window_hwnd:
            raise MapleWindowNotFoundError("Could not find MapleStory window")
        else:
            return window_hwnd

    def ms_get_screen_rect(self, hwnd):
        return win32gui.GetWindowRect(hwnd)

    def capture(self, set_focus=True, hwnd=None, rect=None):
        """Returns Maplestory window screenshot handle(not np.array!)
        : param set_focus boolean : True if MapleStory window is to be focusesd before capture, False if not
        : return : returns Imagegrab of screen"""
        if not hwnd:
            hwnd = self.ms_get_screen_hwnd()
        if not rect:
            rect = self.ms_get_screen_rect(hwnd)
        if set_focus:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
        img = ImageGrab.grab(rect)
        if img:
            return img
        else:
            return 0


class StaticImageProcessor:
    def __init__(self, img_handle=None):
        self.img_handle = img_handle
        self.bgr_img = None
        self.bin_img = None
        self.gray_img = None
        self.processed_img = None
        self.minimap_area = 0
        self.default_minimap_scan_area = [0, 40, 400, 300]
        self.lower_player_marker = np.array([67, 220, 254])  # B G R
        self.upper_player_marker = np.array([69, 222, 255])
        self.hwnd = self.img_handle.ms_get_screen_hwnd()
        self.rect = self.img_handle.ms_get_screen_rect(self.hwnd)

    def update_image(self, src=None, set_focus=True, update_rect=False):
        """src: rgb image data from PIL ImageGrab"""
        if src:
            rgb_img = src
        else:
            if update_rect:
                self.rect = self.img_handle.ms_get_screen_rect(self.hwnd)
            rgb_img = self.img_handle.capture(set_focus, self.hwnd, self.rect)
            if not rgb_img:
                assert self.rgb_img != 0, "self.img_handle did not return img"
        self.bgr_img = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
        self.gray_img = cv2.cvtColor(self.bgr_img, cv2.COLOR_BGR2GRAY)



    def get_minimap_rect(self):
        cropped = self.gray_img[self.default_minimap_scan_area[1]:self.default_minimap_scan_area[3], self.default_minimap_scan_area[0]:self.default_minimap_scan_area[2]]
        blurred_img = cv2.GaussianBlur(cropped, (3,3), 3)
        morphed_img = cv2.erode(blurred_img, (7,7))
        canny = cv2.Canny(morphed_img, threshold1=180, threshold2=255)

        im2, contours, hierachy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            biggest_contour = max(contours, key = cv2.contourArea)
            if cv2.contourArea(biggest_contour) >= 100 and cv2.contourArea(biggest_contour) >= self.minimap_area and cv2.contourArea(biggest_contour) <= 30000:
                minimap_coords = cv2.boundingRect(biggest_contour)
                if minimap_coords[0] > 0 and minimap_coords[1] > 0 and minimap_coords[2] > 0 and minimap_coords[2] > 0:
                    contour_area = cv2.contourArea(biggest_contour)
                    self.minimap_area = contour_area
                    minimap_coords = [minimap_coords[0], minimap_coords[1], minimap_coords[2], minimap_coords[3]]
                    minimap_coords[0] += self.default_minimap_scan_area[0]
                    minimap_coords[1] += self.default_minimap_scan_area[1]
                    return minimap_coords
                else:
                    pass


        return 0

    def reset_minimap_area(self):
        self.minimap_area = 0

    def find_player_minimap_marker(self, rect=None):
        if not rect:
            rect = self.get_minimap_rect()
        assert rect, "Invalid minimap coordinates"
        cropped = self.bgr_img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
        mask = cv2.inRange(cropped, self.lower_player_marker, self.upper_player_marker)
        td = np.transpose(np.where(mask > 0)).tolist()
        if len(td) > 0:
            avg_x = 0
            avg_y = 0
            totalpoints = 0
            for coord in td:
                avg_y += coord[0]
                avg_x += coord[1]
                totalpoints += 1
            avg_y = int(avg_y / totalpoints)
            avg_x = int(avg_x / totalpoints)
            return avg_x, avg_y

        return 0

    def find_other_player_marker(self, rect=None):
        if not rect:
            rect = self.get_minimap_rect()
        assert rect, "Invalid minimap coordinates"
        cropped = self.bgr_img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
        mask = cv2.inRange(cropped, (0, 0, 255), (0, 0, 255))
        td = np.transpose(np.where(mask > 0)).tolist()
        if len(td) > 0:
            avg_x = 0
            avg_y = 0
            totalpoints = 0
            for coord in td:
                avg_y += coord[0]
                avg_x += coord[1]
                totalpoints += 1
            avg_y = int(avg_y / totalpoints)
            avg_x = int(avg_x / totalpoints)
            return avg_x, avg_y

        return 0

