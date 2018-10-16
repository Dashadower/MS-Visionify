import cv2

class MonsterDetector:
    def __init__(self):
        pass

    def find(self, ref_img_path, src_gray_img):
        monster_template_img = cv2.imread(ref_img_path, 0)
        template_matcher = cv2.matchTemplate(src_gray_img, monster_template_img, cv2.TM_CCOEFF_NORMED)