from src.screen_processor import StaticImageProcessor, MapleScreenCapturer
import cv2

wincap = MapleScreenCapturer()
scrp = StaticImageProcessor(wincap)
scrp.update_image()
area = scrp.get_minimap_rect()
while True:
    scrp.update_image(set_focus=False)
    #print("minimap area", area)

    if not area == 0:
        cv2.imshow("test", cv2.cvtColor(scrp.rgb_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]], cv2.COLOR_BGR2RGB))
        print(scrp.find_player_minimap_marker(area))
    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()