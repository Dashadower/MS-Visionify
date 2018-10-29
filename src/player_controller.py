from directinput_constants import DIK_RIGHT, DIK_DOWN, DIK_LEFT, DIK_UP, DIK_ALT, DIK_1
import time, math
# simple jump vertical distance: about 6 pixels

class PlayerController:
    def __init__(self, key_mgr, img_handle):
        self.x = None
        self.y = None

        self.key_mgr = key_mgr
        self.image_handler = img_handle
        self.goal_x = None
        self.goal_y = None

        self.busy = False
        self.mode = None

        self.finemode_limit = 4
        self.horizontal_goal_offset = 5

        self.demonstrike_min_distance = 18

        self.horizontal_jump_distance = 10
        self.horizontal_jump_height = 9


    def calculate_jump_curve(self, coord_x, start_x, start_y, orient):
        """Quadratic jump curve simulation
        : param coord_x : x input in function f(x)
        : param start_x : start x coordinate of jump
        : param start_y : start y coordinate of jump
        : param orient : direction of jump, either jmpr or jmpl"""
        a = 0.3
        if orient == "jmpr":
            y = a * ((coord_x - (start_x+self.horizontal_jump_distance/2)) ** 2) + start_y - self.horizontal_jump_height
            return round(y, 2)
        elif orient == "jmpl":
            y = a * ((coord_x - (start_x-self.horizontal_jump_distance/2)) ** 2) + start_y - self.horizontal_jump_height
            return round(y, 2)

        return 0

    def quadratic_platform_jump(self, goal_platform, jmp_range_start, jmp_range_end, **kwargs):
        """Use quadratic to simulate jump and determine x coordinate required to move
        : param goal_coord : tuple((x,y), (x,y)) of goal platform start and end
        : param jmp_range_start : tuple(x,y) of minimum movable current platform
        : param jmp_range_end : tuple(x,y) of maximum movable current platform"""

        # to determine which end we are going to use as goal coordinate, calculate SED of each point
        d1 = (self.x-goal_platform[0][0]) ** 2
        d2 = (self.x-goal_platform[1][0]) ** 2
        if d1 < d2:
            goal_x, goal_y = goal_platform[0][0], goal_platform[0][1]
        else:
            goal_x, goal_y = goal_platform[1][0], goal_platform[1][1]

        min_platform_x = min(jmp_range_start, jmp_range_end)
        max_platform_x = max(jmp_range_start, jmp_range_end)

        if goal_x - self.x > 0:
            mode = "jmpr"
        elif goal_x - self.x < 0:
            mode = "jmpl"

        minimum_jmp_x = None
        print("quadratic: current location: %d %d"%(self.x, self.y), "destination %d %d"%(goal_x, goal_y))
        if mode == "jmpl":
            for x in range(self.x-1, min_platform_x, -1):
                platform_function_height = int(self.calculate_jump_curve(goal_x, x, self.y, mode))
                print("y coord at x coord %d: %d"%(x, platform_function_height))
                if platform_function_height <= goal_y and platform_function_height != 0 and platform_function_height > 0:
                    minimum_jmp_x = x
                    break
        elif mode == "jmpr":
            for x in range(self.x+1, max_platform_x):
                platform_function_height = int(self.calculate_jump_curve(goal_x, x, self.y, mode))
                print("y coord at x coord %d: %d" % (x, platform_function_height))
                if platform_function_height <= goal_y  and platform_function_height != 0 and platform_function_height > 0:
                    minimum_jmp_x = x
                    break
        if not minimum_jmp_x:
            print("no solution found")
        else:
            print("quadratic: move from %d to %d"%(self.x, int(minimum_jmp_x)))
            self.horizontal_move_goal(minimum_jmp_x, blocking=True)


    def precise_horizontal_move_goal(self, goal_x, blocking=False):
        if goal_x - self.x > 0:
            # need to go right:
            mode = "r"
        else:
            # need to go left:
            mode = "l"
        finemode = False
        if mode == "r":
            if self.x >= goal_x - self.finemode_limit:
                finemode = True
        elif mode == "l":
            if self.x <= goal_x + self.finemode_limit:
                finemode = True
        if not finemode:
            if mode == "r":
                # need to go right:
                self.key_mgr._direct_press(DIK_RIGHT)
            elif mode == "l":
                # need to go left:
                self.key_mgr._direct_press(DIK_LEFT)
        while True:
            self.image_handler.update_image()
            self.x = self.image_handler.find_player_minimap_marker(self.image_handler.minimap_rect)
            if not self.x:
                continue
            if self.x:
                self.x = self.x[0]
            if finemode:
                if mode == "r":
                    self.key_mgr._direct_press(DIK_RIGHT)
                    time.sleep(0.03)
                    self.key_mgr._direct_release(DIK_RIGHT)
                elif mode == "l":
                    self.key_mgr._direct_press(DIK_LEFT)
                    time.sleep(0.03)
                    self.key_mgr._direct_release(DIK_LEFT)
                time.sleep(0.05)
            if mode == "r":
                if self.x >= goal_x-self.finemode_limit:
                    finemode = True
                if self.x >= goal_x-self.horizontal_goal_offset:
                    break
            elif mode == "l":
                if self.x <= goal_x+self.finemode_limit:
                    finemode = True
                if self.x <= goal_x+self.horizontal_goal_offset:
                    break
            if goal_x - self.x > 0:
                # need to go right:
                mode = "r"
            else:
                # need to go left:
                mode = "l"
        self.key_mgr.reset()

    def horizontal_move_goal(self, goal_x, blocking=False):
        if goal_x - self.x > 0:
            # need to go right:
            mode = "r"
        elif goal_x - self.x < 0:
            # need to go left:
            mode = "l"
        else:
            return 0
        """?if abs(goal_x - self.x) >= self.demonstrike_min_distance:
            if mode == "r":
                self.key_mgr.single_press(DIK_RIGHT)
                time.sleep(0.05)
                while True:
                    self.image_handler.update_image()
                    self.x = self.image_handler.find_player_minimap_marker(self.image_handler.minimap_rect)[0]
                    print(goal_x, self.x)
                    self.key_mgr.single_press(DIK_1)
                    if abs(goal_x - self.x) <= self.demonstrike_min_distance or goal_x <= self.x:
                        break
                    time.sleep(0.2)
            elif mode == "l":
                self.key_mgr.single_press(DIK_LEFT)
                time.sleep(0.05)
                while True:
                    self.image_handler.update_image()
                    self.x = self.image_handler.find_player_minimap_marker(self.image_handler.minimap_rect)[0]
                    print(goal_x, self.x)
                    self.key_mgr.single_press(DIK_1)
                    if abs(goal_x - self.x) <= self.demonstrike_min_distance or goal_x >= self.x:
                        break
                    time.sleep(0.2)"""

        if goal_x - self.x > 0:
            # need to go right:
            mode = "r"
        elif goal_x - self.x < 0:
            # need to go left:
            mode = "l"            
        
        if mode == "r":
            # need to go right:
            self.key_mgr._direct_press(DIK_RIGHT)
        elif mode == "l":
            # need to go left:
            self.key_mgr._direct_press(DIK_LEFT)
        while True:
            self.image_handler.update_image()
            self.x = self.image_handler.find_player_minimap_marker(self.image_handler.minimap_rect)[0]
            if not self.x:
                assert 1 == 0, "horizontal_move goal: failed to recognize coordinates"

            if mode == "r":
                if self.x >= goal_x-self.horizontal_goal_offset:
                    self.key_mgr._direct_release(DIK_RIGHT)
                    break
            elif mode == "l":
                if self.x <= goal_x+self.horizontal_goal_offset:
                    self.key_mgr._direct_release(DIK_LEFT)
                    break
        self.key_mgr.reset()



    def dbljump_max(self):
        """Warining: is a blocking call"""
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_ALT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr._direct_release(DIK_UP)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr._direct_release(DIK_UP)

    def jumpl(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_LEFT)
        self.key_mgr._direct_release(DIK_ALT)

    def jumpl_double(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.05)
        self.key_mgr._direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_release(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_release(DIK_LEFT)

    def jumpl_glide(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.15)
        self.key_mgr._direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.2)
        self.key_mgr._direct_release(DIK_ALT)
        self.key_mgr._direct_release(DIK_LEFT)

    def jumpr(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_RIGHT)
        self.key_mgr._direct_release(DIK_ALT)

    def jumpr_double(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.05)
        self.key_mgr._direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_release(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_release(DIK_RIGHT)


    def jumpr_glide(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.15)
        self.key_mgr._direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.2)
        self.key_mgr._direct_release(DIK_ALT)
        self.key_mgr._direct_release(DIK_RIGHT)

    def drop(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_DOWN)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_DOWN)
        self.key_mgr._direct_release(DIK_ALT)

    def update(self, pcoord):
        self.x, self.y = pcoord
        if self.goal_x and self.mode == "r":
            if self.x >= self.goal_x:
                self.busy = False
                self.key_mgr.reset()
        elif self.goal_x and self.mode == "l":
            if self.x <= self.goal_x:
                self.key_mgr.reset()
                self.busy = False


