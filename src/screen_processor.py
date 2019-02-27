import cv2, win32gui, time, math, win32ui, win32con
from PIL import ImageGrab
import numpy as np, ctypes, ctypes.wintypes

class MapleWindowNotFoundError(Exception):
    pass


MAPLESTORY_WINDOW_TITLE = "MapleStory"





class MapleScreenCapturer:
    """Container for capturing MS screen"""
    def __init__(self):
        self.hwnd = None

    def ms_get_screen_hwnd(self):
        window_hwnd = win32gui.FindWindow(0, MAPLESTORY_WINDOW_TITLE)
        if not window_hwnd:
            return 0
        else:
            return window_hwnd

    def ms_get_screen_rect(self, hwnd):
        """
        Added compatibility code from
        https://stackoverflow.com/questions/51786794/using-imagegrab-with-bbox-from-pywin32s-getwindowrect
        :param hwnd: window handle from self.ms_get_screen_hwnd
        :return: window rect (x1, y1, x2, y2) of MS rect.
        """
        try:
            f = ctypes.windll.dwmapi.DwmGetWindowAttribute
        except WindowsError:
            f = None
        if f:  # Vista & 7 stuff
            rect = ctypes.wintypes.RECT()
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            f(ctypes.wintypes.HWND(self.ms_get_screen_hwnd()),
              ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
              ctypes.byref(rect),
              ctypes.sizeof(rect)
              )
            size = (rect.left, rect.top, rect.right, rect.bottom)
        else:
            if not hwnd:
                hwnd = self.ms_get_screen_hwnd()
            size = win32gui.GetWindowRect(hwnd)
        return size  # returns x1, y1, x2, y2

    def capture(self, set_focus=True, hwnd=None, rect=None):
        """Returns Maplestory window screenshot handle(not np.array!)
        :param set_focus : True if MapleStory window is to be focusesd before capture, False if not
        :param hwnd : Default: None Win32API screen handle to use. If None, sets and uses self.hwnd
        :param rect : If defined, captures specificed ScreenRect area (x1, y1, x2, y2). Else, uses MS window ms_screen_rect.
        :return : returns Imagegrab of screen (PIL Image)"""
        if hwnd:
            self.hwnd = hwnd
        if not hwnd:
            self.hwnd = self.ms_get_screen_hwnd()
        if not rect:
            rect = self.ms_get_screen_rect(self.hwnd)
        if set_focus:
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
        img = ImageGrab.grab(rect)
        return img

    def screen_capture(self,w, h, x=0, y=0, save=True, save_name=''):
        # hwnd = win32gui.FindWindow(None, None)
        hwnd = win32gui.GetDesktopWindow()
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (w, h), dcObj, (x, y), win32con.SRCCOPY)

        if save:
            dataBitMap.SaveBitmapFile(cDC, save_name)
        else:
            b = dataBitMap.GetBitmapBits(True)
            img = np.fromstring(b, np.uint8).reshape(h, w, 4)
            cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        if not save:
            return img

    def pil_image_to_array(self, img):
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

class StaticImageProcessor:
    def __init__(self, img_handle=None):
        """

        :param img_handle: handle to MapleScreenCapturer
        """
        if not img_handle:
            raise Exception("img_handle must reference an MapleScreenCapturer class!!")

        self.img_handle = img_handle
        self.bgr_img = None
        self.bin_img = None
        self.gray_img = None
        self.processed_img = None
        self.minimap_area = 0
        self.minimap_rect = None

        self.maximum_minimap_area = 40000

        self.default_minimap_scan_area = [0, 60, 400, 300]  # x1, y1, x2, y2

        # Minimap player marker original BGR: 68, 221, 255
        self.lower_player_marker = np.array([67, 220, 254])  # B G R
        self.upper_player_marker = np.array([69, 222, 256])
        self.lower_rune_marker = np.array([254, 101, 220]) # B G R
        self.upper_rune_marker = np.array([255, 103, 222])

        self.hwnd = self.img_handle.ms_get_screen_hwnd()
        self.ms_screen_rect = None
        if self.hwnd:
            self.ms_screen_rect = self.img_handle.ms_get_screen_rect(self.hwnd)

        else:
            raise Exception("Could not find MapleStory window!!")



    def update_image(self, src=None, set_focus=True, update_rect=False):
        """
        Calls ScreenCapturer's update function and updates images.
        :param src : rgb image data from PIL ImageGrab
        :param set_focus : True if win32api setfocus shall be called before capturing"""
        if src:
            rgb_img = src
        else:
            if update_rect:
                self.ms_screen_rect = self.img_handle.ms_get_screen_rect(self.hwnd)

            if not self.ms_screen_rect:
                self.ms_screen_rect = self.img_handle.ms_get_screen_rect(self.hwnd)
            rgb_img = self.img_handle.capture(set_focus, self.hwnd, self.ms_screen_rect)
            if not rgb_img:
                assert self.bgr_img != 0, "self.img_handle did not return img"
        self.bgr_img = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
        self.gray_img = cv2.cvtColor(self.bgr_img, cv2.COLOR_BGR2GRAY)

    def get_minimap_rect(self):
        """
        Processes self.gray images, returns minimap bounding box
        :return: Array [x,y,w,h] bounding box of minimap if found, else 0
        """
        cropped = self.gray_img[self.default_minimap_scan_area[1]:self.default_minimap_scan_area[3], self.default_minimap_scan_area[0]:self.default_minimap_scan_area[2]]
        blurred_img = cv2.GaussianBlur(cropped, (3,3), 3)
        morphed_img = cv2.erode(blurred_img, (7,7))
        canny = cv2.Canny(morphed_img, threshold1=180, threshold2=255)
        try:
            im2, contours, hierachy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        except:
            contours, hierachy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            biggest_contour = max(contours, key = cv2.contourArea)
            if cv2.contourArea(biggest_contour) >= 100 and cv2.contourArea(biggest_contour) >= self.minimap_area and cv2.contourArea(biggest_contour) <= self.maximum_minimap_area:
                minimap_coords = cv2.boundingRect(biggest_contour)
                if minimap_coords[0] > 0 and minimap_coords[1] > 0 and minimap_coords[2] > 0 and minimap_coords[2] > 0:
                    contour_area = cv2.contourArea(biggest_contour)
                    self.minimap_area = contour_area
                    minimap_coords = [minimap_coords[0], minimap_coords[1], minimap_coords[2], minimap_coords[3]]
                    minimap_coords[0] += self.default_minimap_scan_area[0]
                    minimap_coords[1] += self.default_minimap_scan_area[1]
                    self.minimap_rect = minimap_coords
                    return minimap_coords
                else:
                    pass

        return 0

    def reset_minimap_area(self):
        """
        Resets self.minimap_area which is used to reset self.get_minimap_rect search.
        :return: None
        """
        self.minimap_area = 0

    def find_player_minimap_marker(self, rect=None):
        """
        Processes self.bgr_image to return player coordinate on minimap.
        The player marker has exactly 12 pixels of the detection color to form a pixel circle(2,4,4,2 pixels). Therefore
        before calculation the mean pixel value of the mask, we remove "false positives", which are not part of the
        player color by finding pixels which do not have between 10 to 12 other pixels(including itself) of the same color in a
        distance of 3.
        :param rect: [x,y,w,h] bounding box of minimap in MapleStory screen. Call self.get_minimap_rect to obtain
        :return: x,y coordinate of player relative to ms_screen_rect if found, else 0
        """
        if not rect and not self.minimap_rect:
            rect = self.get_minimap_rect()
        else:
            rect = self.minimap_rect

        assert rect, "Invalid minimap coordinates"

        cropped = self.bgr_img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
        mask = cv2.inRange(cropped, self.lower_player_marker, self.upper_player_marker)
        td = np.transpose(np.where(mask > 0)).tolist()

        if len(td) > 0:
            avg_x = 0
            avg_y = 0
            totalpoints = 0
            for coord in td:
                nearest_points = 0  # Points which are close to coord pixel
                for ref_coord in td:
                    # Calculate the range between every single pixel
                    if math.sqrt(abs(ref_coord[0]-coord[0])**2 + abs(ref_coord[1]-coord[1])**2) <= 3:
                        nearest_points += 1

                if nearest_points >= 10 and nearest_points <= 13:
                    avg_y += coord[0]
                    avg_x += coord[1]
                    totalpoints += 1

            if totalpoints == 0:
                return 0

            avg_y = int(avg_y / totalpoints)
            avg_x = int(avg_x / totalpoints)
            return avg_x, avg_y

        return 0



    def find_other_player_marker(self, rect=None):
        """
        Processes self.bgr_image to return coordinate of other players on minimap if exists.
        Does not behave as expected when there are more than one other player on map. Use this function to just detect.
        :param rect: [x,y,w,h] bounding box of minimap. Call self.get_minimap_rect
        :return: x,y coord of marker if found, else 0
        """
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

    def find_rune_marker(self, rect=None):
        """
        Processes self.bgr_image to return coordinates of rune marker on minimap.
        :param rect: [x,y,w,h] bounding box of minimap. Call self.get_minimap_rect
        :return: x,y of rune minimap coordinates if found, else 0
        """
        if not rect and not self.minimap_rect:
            rect = self.get_minimap_rect()
        else:
            rect = self.minimap_rect
        assert rect, "Invalid minimap coordinates"
        cropped = self.bgr_img[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
        mask = cv2.inRange(cropped, self.lower_rune_marker, self.upper_rune_marker)
        td = np.transpose(np.where(mask > 0)).tolist()
        if len(td) > 0:
            avg_x = 0
            avg_y = 0
            totalpoints = 0
            for coord in td:
                nearest_points = 0  # Points which are close to coord pixel
                for ref_coord in td:
                    # Calculate the range between every single pixel
                    if math.sqrt(abs(ref_coord[0] - coord[0]) ** 2 + abs(ref_coord[1] - coord[1]) ** 2) <= 6:
                        nearest_points += 1

                if nearest_points >= 20 and nearest_points <= 25:
                    avg_y += coord[0]
                    avg_x += coord[1]
                    totalpoints += 1

            if totalpoints == 0:
                return 0

            avg_y = int(avg_y / totalpoints)
            avg_x = int(avg_x / totalpoints)
            return avg_x, avg_y

        return 0

if __name__ == "__main__":
    dx = MapleScreenCapturer()
    hwnd = dx.ms_get_screen_hwnd()
    rect = dx.ms_get_screen_rect(hwnd)
    dx.capture(rect=rect)
