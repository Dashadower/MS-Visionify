from directinput_constants import DIK_RIGHT, DIK_DOWN, DIK_LEFT, DIK_UP, DIK_ALT
import time, math
# simple jump vertical distance: about 6 pixels

class PlayerController:
    def __init__(self, key_mgr):
        self.x = None
        self.y = None

        self.key_mgr = key_mgr
        self.goal_x = None
        self.goal_y = None

        self.busy = False
        self.mode = None

        self.finemode_limit = 5
        self.horizontal_goal_offset = 2

        self.horizontal_jump_distance = 8
        self.horizontal_jump_height = 7
    def calculate_jump_curve(self, coord_x, start_x, start_y, orient):
        """Quadratic jump curve simulation
        : param coord_x : x input in function f(x)
        : param start_x : start x coordinate of jump
        : param start_y : start y coordinate of jump
        : param orient : direction of jump, either jmpr or jmpl"""
        if orient == "jmpr":
            y = 0.4 * ((coord_x - (start_x+self.horizontal_jump_distance/2)) ** 2) + start_y - self.horizontal_jump_height
            return y
        elif orient == "jmpl":
            y = 0.4 * ((coord_x - (start_x-self.horizontal_jump_distance/2)) ** 2) + start_y - self.horizontal_jump_height
            return y

        return 0

    def quadratic_platform_jump(self, goal_platform, jmp_range_start, jmp_range_end):
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
                platform_function_height = int(self.calculate_jump_curve(goal_x, self.x, self.y, mode))
                print("y coord at x coord %d: %d"%(x, platform_function_height))
                if platform_function_height < goal_y - 2 and platform_function_height != 0 and platform_function_height > 0:
                    minimum_jmp_x = x
                    break
        elif mode == "jmpr":
            for x in range(self.x+1, max_platform_x):
                platform_function_height = int(self.calculate_jump_curve(goal_x, self.x, self.y, mode))
                print("y coord at x coord %d: %d" % (x, platform_function_height))
                if platform_function_height < goal_y - 2 and platform_function_height != 0 and platform_function_height > 0:
                    minimum_jmp_x = x
                    break
        print("quadratic: move from %d to %d"%(self.x, int(minimum_jmp_x)))
        self.horizontal_move_goal(minimum_jmp_x)

    def horizontal_move_goal(self, goal_x, blocking=False, pos_func=None, pos_func_args=None):
        if blocking:
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
                if goal_x - self.x > 0:
                    # need to go right:
                    mode = "r"
                    self.key_mgr._direct_press(DIK_RIGHT)
                else:
                    # need to go left:
                    mode = "l"
                    self.key_mgr._direct_press(DIK_LEFT)
            while True:
                pos_func.update_image()
                self.x = pos_func.find_player_minimap_marker(pos_func_args)[0]
                if finemode:
                    if mode == "r":
                        self.key_mgr._direct_press(DIK_RIGHT)
                        time.sleep(0.03)
                        self.key_mgr._direct_release(DIK_RIGHT)
                    elif mode == "l":
                        self.key_mgr._direct_press(DIK_LEFT)
                        time.sleep(0.03)
                        self.key_mgr._direct_release(DIK_LEFT)
                    time.sleep(0.1)
                if mode == "r":
                    if self.x >= goal_x-self.finemode_limit:
                        finemode = True
                    if self.x >= goal_x-self.horizontal_goal_offset:
                        break
                elif mode == "l":
                    if self.x <= goal_x+self.finemode_limit:
                        finemode = True
                    if self.x <= goal_x-self.horizontal_goal_offset:
                        break
            self.key_mgr.reset()

        else:
            if self.x != goal_x:
                self.goal_x = goal_x
                self.busy = True
                if goal_x - self.x > 0:
                    # need to go right:
                    self.mode = "r"
                    self.key_mgr.set_key_state(DIK_RIGHT, 1)

                else:
                    # need to go right:
                    self.mode = "l"
                    self.key_mgr.set_key_state(DIK_LEFT, 1)

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

    def jumpr(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_RIGHT)
        self.key_mgr._direct_release(DIK_ALT)

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


"""dt = PlayerController("asf")
for x in range(47, 64):
    print(dt.calculate_jump_curve(72, 64, 52, "jmpr"))"""
