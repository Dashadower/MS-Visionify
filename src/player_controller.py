from directinput_constants import DIK_RIGHT, DIK_DOWN, DIK_LEFT, DIK_UP, DIK_ALT
import time


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


