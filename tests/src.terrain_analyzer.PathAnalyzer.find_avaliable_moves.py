import sys
sys.path.append("../")
sys.path.append("../src") # just in case we're outside IDE
try:
    from src.screen_processor import StaticImageProcessor, MapleScreenCapturer
    from src.terrain_analyzer import PathAnalyzer
    from src.keystate_manager import KeyboardInputManager
    from src.player_controller import PlayerController
    from src.directinput_constants import DIK_A, DIK_Q, DIK_D, DIK_F
except ImportError:
    from screen_processor import StaticImageProcessor, MapleScreenCapturer
    from terrain_analyzer import PathAnalyzer
    from keystate_manager import KeyboardInputManager
    from player_controller import PlayerController
    from directinput_constants import DIK_A, DIK_Q, DIK_D, DIK_F    
from win32gui import SetForegroundWindow
import cv2, imutils, time, random, os

keybd_mgr = KeyboardInputManager()

wincap = MapleScreenCapturer()
scrp = StaticImageProcessor(wincap)
scrp.update_image()
player_mgr = PlayerController(keybd_mgr, scrp)
area = scrp.get_minimap_rect()
pathextractor = PathAnalyzer()
savemode = 1
while True:
    scrp.update_image(set_focus=False)
    playerpos = 0
    if not area:
        area = scrp.get_minimap_rect()
    if area:
        playerpos = scrp.find_player_minimap_marker(area)
    if playerpos:
        if savemode:
            pathextractor.input(playerpos[0], playerpos[1])
        else:
            pathextractor.input_oneway_platform(playerpos[0], playerpos[1])
    cropped_img = scrp.bgr_img[area[1]:area[1] + area[3], area[0]:area[0] + area[2]]
    if playerpos:
        cv2.circle(cropped_img, playerpos, 5, (0,255,0), -1)
    if pathextractor.platforms:
        for platform in pathextractor.platforms:
            cv2.line(cropped_img, platform[0], platform[1], (0, 255, 0), 1)
            cv2.circle(cropped_img, platform[0], 2, (0,0,255), -1)
            cv2.circle(cropped_img, platform[1], 2, (0, 0, 255), -1)
    if pathextractor.oneway_platforms:
        for platform in pathextractor.oneway_platforms:
            cv2.line(cropped_img, platform[0], platform[1], (255, 0, 0), 1)
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
    elif inp == ord("s"):
        pathextractor.save(minimap_roi=area)
    elif inp == ord("t"):
        print("now recording oneway platform")
        savemode = 0

if os.path.exists("mapdata.platform"):
    if input("map data exists. load that instead?(y if yes)") == "y":
        mcoords = pathextractor.load()
        if mcoords:
            area = mcoords
        print("loaded platform data:", pathextractor.platforms)
print("path processing done")
time.sleep(0.5)
SetForegroundWindow(wincap.ms_get_screen_hwnd())
time.sleep(0.5)
cplatform = None
last_visited = None
exceed_count = 0
last_thousand_sword_time = time.time()
while True:
    cplatform = None
    print("-" * 10)
    scrp.update_image(set_focus=False)
    cpos = scrp.find_player_minimap_marker(area)
    if cpos:
        player_mgr.update(cpos)
        print("current minimap coord", cpos)
        for platform in pathextractor.platforms:
            if cpos[0] <= platform[1][0] and cpos[0] >= platform[0][0] and cpos[1] == platform[1][1]:
                cplatform = platform
                break
        if not cplatform:
            for platform in pathextractor.oneway_platforms:
                if cpos[0] <= platform[1][0] and cpos[0] >= platform[0][0] and cpos[1] == platform[1][1]:
                    cplatform = platform
                    print("at oneway platform")
                    break
        if cplatform:

            print("current platform:", cplatform)
            solutions = pathextractor.find_available_moves(cplatform)
            other_solutions = []
            if last_visited:
                if len(solutions) > 1:
                    for p in solutions:
                        if p[0] == last_visited:
                            pass
                        else:
                            other_solutions.append(p)
                else:
                    other_solutions = solutions
            elif not last_visited:
                other_solutions = solutions
            #print("avaliable solutions:", other_solutions)
            #print("last visited:", last_visited)
            solution = random.choice(other_solutions)
            last_visited = cplatform

            print("moving to", solution[0])
            #SetForegroundWindow(wincap.ms_get_screen_hwnd())
            time.sleep(0.1)
            if cpos[0] < solution[1][0] or cpos[0] > solution[2][0]:
                cpos = scrp.find_player_minimap_marker(area)
                player_mgr.update(cpos)
                #keybd_mgr.reset()
                time.sleep(0.1)
                player_mgr.horizontal_move_goal(int((solution[1][0]+solution[2][0])/2), blocking=True)
                #player_mgr.quadratic_platform_jump(solution[0], solution[1][0], solution[2][0], area)
            print("horizontal movement done")
            time.sleep(0.3)

            if solution[3] == "jmpl":
                player_mgr.jumpl_double()
                time.sleep(1)
            elif solution[3] == "jmpr":
                player_mgr.jumpr_double()
                time.sleep(1)
            elif solution[3] == "drop":
                player_mgr.drop()
                time.sleep(1)
            elif solution[3] == "dbljmp":
                player_mgr.dbljump_max()
                time.sleep(1)



            if abs(last_thousand_sword_time-time.time()) >= 10 + random.randint(1, 6):
                keybd_mgr.single_press(DIK_F)
                last_thousand_sword_time = time.time()
                exceed_count += 5
                time.sleep(1)
            else:
                keybd_mgr.single_press(DIK_A)
                print("PRESS A")
                exceed_count += 1
                time.sleep(0.1)
            
            if exceed_count > 18:
                keybd_mgr.single_press(DIK_Q)
                time.sleep(1)
                exceed_count = 0

            if random.randrange(1, 5) == 1:
                time.sleep(0.5)
                keybd_mgr.single_press(DIK_D)
                print("randomized")
                time.sleep(0.2)
            time.sleep(0.1)
            #keybd_mgr.reset()

        else:
            print("failed to find platform. please reposition")
    else:
        print("failed to read minimap")
