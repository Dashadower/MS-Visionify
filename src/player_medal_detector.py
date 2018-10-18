
import cv2, json, os

class PlayerMedalDetector:
    """Time consuming matchTemplate based mob detector. Uses reference images to compare image screen"""
    def __init__(self):
        self.template = None
        self.medal_data = json.loads(open("img/medals/medals.json", "r", encoding="utf-8").read())
    def create_template(self, template_img_filename):
        """Save reference image to memory"""
        template_img = cv2.imread(os.path.join(self.medal_data["imgdir"], template_img_filename), 0)
        self.template = template_img
        self.template_calibrated_xcoords = self.medal_data[template_img_filename]["offset_x"]
        self.template_calibrated_ycoords = self.medal_data[template_img_filename]["offset_y"]

    def find(self, src_gray_img_arr):
        template_matcher = cv2.matchTemplate(src_gray_img_arr, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_matcher)
        return (max_loc[0]+self.template_calibrated_xcoords, max_loc[1]+self.template_calibrated_ycoords)

