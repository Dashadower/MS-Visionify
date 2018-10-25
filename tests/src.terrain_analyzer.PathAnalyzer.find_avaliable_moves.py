from src.screen_processor import StaticImageProcessor, MapleScreenCapturer
from src.terrain_analyzer import PathAnalyzer
from src.keystate_manager import KeyboardInputManager
from src.player_controller import PlayerController
from win32gui import SetForegroundWindow
import cv2, imutils, time

keybd_mgr = KeyboardInputManager()
player_mgr = PlayerController(keybd_mgr)
wincap = MapleScreenCapturer()
scrp = StaticImageProcessor(wincap)
scrp.update_image()
area = scrp.get_minimap_rect()
pathextractor = PathAnalyzer()

while True:
    scrp.update_image(set_focus=False)
    playerpos = 0
    if not area:
        area = scrp.get_minimap_rect()
    if area:
        playerpos = scrp.find_player_minimap_marker(area)
    if playerpos:
        pathextractor.input(playerpos[0], playerpos[1])

    cropped_img = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]
    if playerpos:
        cv2.circle(cropped_img, playerpos, 5, (0,255,0), -1)
    if pathextractor.platforms:
        for platform in pathextractor.platforms:
            cv2.line(cropped_img, platform[0], platform[1], (0, 255, 0), 1)
            cv2.circle(cropped_img, platform[0], 2, (0,0,255), -1)
            cv2.circle(cropped_img, platform[1], 2, (0, 0, 255), -1)

    cropped_img = imutils.resize(cropped_img, width=500)
    cv2.imshow("test", cropped_img)

    inp = cv2.waitKey(1)
    if inp == ord('q'):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        scrp.reset_minimap_area()
        area = scrp.get_minimap_rect()
        pathextractor.reset()

print("path recording done")
time.sleep(0.5)
cplatform = None
while True:
    scrp.update_image(set_focus=False)
    cpos = scrp.find_player_minimap_marker(area)
    player_mgr.update(cpos)
    print("current minimap coord", cpos)
    for platform in pathextractor.platforms:
        if cpos[0] <= platform[1][0] and cpos[0] >= platform[0][0] and cpos[1] == platform[1][1]:
            cplatform = platform
            break
    if cplatform:
        print("current platform:", cplatform)
        solutions = pathextractor.find_available_moves(cplatform)
        print("avaliable solutions:", solutions)
        choice = input("select index to move:")
        if not choice.isdigit():
            print("wrong selection")
            continue

        solution = solutions[int(choice)]
        print("moving to", solution[0])
        time.sleep(0.5)
        SetForegroundWindow(wincap.ms_get_screen_hwnd())
        time.sleep(1)
        if cpos[0] < solution[1][0] or cpos[0] > solution[2][0]:
            #player_mgr.horizontal_move_goal(int((solution[1][0]+solution[2][0])/2), blocking=True, pos_func=scrp, pos_func_args=area)
            player_mgr.quadratic_platform_jump(solution[0], solution[1][0], solution[2][0])
        print("horizontal movement done")
        time.sleep(0.5)
        if solution[3] == "jmpl":
            player_mgr.jumpl()
        elif solution[3] == "jmpr":
            player_mgr.jumpr()
        elif solution[3] == "drop":
            player_mgr.drop()
        elif solution[3] == "dbljmp":
            player_mgr.dbljump_max()
        time.sleep(2)

