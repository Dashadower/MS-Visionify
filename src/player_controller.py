from directinput_constants import DIK_RIGHT, DIK_DOWN, DIK_LEFT, DIK_UP, DIK_ALT
from keystate_manager import DEFAULT_KEY_MAP
import time, math
# simple jump vertical distance: about 6 pixels

class PlayerController:
    """
    This class keeps track of character location and manages advanced movement and attacks.
    """
    def __init__(self, key_mgr, screen_handler, keymap=DEFAULT_KEY_MAP):
        """
        Class Variables:
        self.x: Known player minimap x coord. Needs to be updated manually
        self.x: Known player minimap y coord. Needs tobe updated manually
        self.key_mgr: handle to KeyboardInputManager
        self.screen_processor: handle to StaticImageProcessor
        self.goal_x: If moving, destination x coord
        self.goal_y: If moving, destination y coord
        self.busy: True if current class is calling blocking calls or in a loop
        :param key_mgr: Handle to KeyboardInputManager
        :param screen_handler: Handle to StaticImageProcessor. Only used to call find_player_minimap_marker
        """
        self.x = None
        self.y = None

        self.keymap = keymap
        self.jump_key = self.keymap["jump"]
        self.key_mgr = key_mgr
        self.screen_processor = screen_handler
        self.goal_x = None
        self.goal_y = None

        self.busy = False

        self.finemode_limit = 4
        self.horizontal_goal_offset = 5

        self.demonstrike_min_distance = 18

        self.horizontal_jump_distance = 10
        self.horizontal_jump_height = 9

        self.x_movement_enforce_rate = 10  # refer to optimized_horizontal_move

        self.moonlight_slash_x_range = 30  # exceed: moonlight slash's estimalte x hitbox range in minimap coords.



    def calculate_jump_curve(self, coord_x, start_x, start_y, orient):
        """Quadratic jump curve simulation
        :param coord_x : x input in function f(x)
        :param start_x : start x coordinate of jump
        :param start_y : start y coordinate of jump
        :param orient : direction of jump, either jmpr or jmpl"""
        a = 0.3
        if orient == "jmpr":
            y = a * ((coord_x - (start_x+self.horizontal_jump_distance/2)) ** 2) + start_y - self.horizontal_jump_height
            return round(y, 2)
        elif orient == "jmpl":
            y = a * ((coord_x - (start_x-self.horizontal_jump_distance/2)) ** 2) + start_y - self.horizontal_jump_height
            return round(y, 2)

        return 0

    def quadratic_platform_jump(self, goal_platform, jmp_range_start, jmp_range_end, **kwargs):
        """
        Use quadratic to simulate jump and determine x coordinate required to move
        :param goal_coord : tuple((x,y), (x,y)) of goal platform start and end
        :param jmp_range_start : tuple(x,y) of minimum movable current platform
        :param jmp_range_end : tuple(x,y) of maximum movable current platform"""

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
            self.horizontal_move_goal(minimum_jmp_x)

    def linear_glide(self, x, jmp_x, jmp_y, jmp_height, slope):
        """
        Calculates glide y coordinate at x coordinate x with input constants
        :param x: Desired X coordinate to get Y coordinates
        :param jmp_x: Origin of glide X coordinates
        :param jmp_y: Origin of glide Y coordinates
        :param jmp_height: Standard single jump height
        :param slope: Glide coefficient. Recommended: -0.2 for left, 0.2 for right
        :return: Y coordinate
        """
        b = jmp_y - jmp_height - slope * jmp_x
        y = slope * x + b
        return y

    def optimized_horizontal_move(self, goal_x, ledge=False, enforce_time=True):
        """
        Move from self.x to goal_x in as little time as possible. Uses multiple movement solutions for efficient paths. Blocking call
        :param goal_x: x coordinate to move to. This function only takes into account x coordinate movements.
        :param ledge: If true, goal_x is an end of a platform, additional movement solutions can be used. If not, precise movement is required.
        :param enforce_time: If true, the function will stop moving after a time threshold is met and still haven't
        met the goal. Default threshold is 15 minimap pixels per second. Fail-safe implementation.
        :return: None
        """
        glide_threshold = 30
        glide_goal_offset = 15
        walk_goal_offset = 3

        loc_delta = self.x - goal_x
        abs_loc_delta = abs(loc_delta)
        start_time = time.time()
        if loc_delta < 0:
            # we need to move right
            time_limit = math.ceil(abs_loc_delta/self.x_movement_enforce_rate) + 1
            if ledge:
                self.key_mgr.single_press(DIK_RIGHT, 0.1)
                while True:
                    if time.time()-start_time > time_limit and enforce_time:
                        break
                    self.key_mgr.single_press(self.keymap["demon_strike"])
                    self.screen_processor.update_image()
                    player_pos = self.screen_processor.find_player_minimap_marker()
                    self.update(player_pos[0], player_pos[1])
                    if player_pos[0] >= goal_x:
                        return 0  # We can just exit function since we demon strike stops on ledges
            if abs_loc_delta <= glide_threshold:
                # Just walk if distance is less than 10 pixels
                self.key_mgr.direct_press(DIK_RIGHT)

                # Below: use a loop to continuously press right until goal is reached or time is up
                while True:
                    if time.time()-start_time > time_limit and enforce_time:
                        break
                    self.screen_processor.update_image()
                    player_pos = self.screen_processor.find_player_minimap_marker()
                    self.update(player_pos[0], player_pos[1])
                    # Problem with synchronizing player_pos with self.x and self.y. Needs to get resolved.
                    # Current solution: Just call self.update() (not good for redundancy)
                    if player_pos[0] >= goal_x - walk_goal_offset:
                        # Reached or exceeded destination x coordinates
                        print(player_pos, goal_x)
                        break

                self.key_mgr.direct_release(DIK_RIGHT)

            else:
                # Distance is quite big, so we glide
                # Note: Even if we release keys and stop gliding, MS keeps the character's momentum, so we need to stop prematurely
                self.key_mgr.direct_press(DIK_RIGHT)
                self.key_mgr.single_press(self.jump_key, 0.3)
                self.key_mgr.direct_press(self.jump_key)
                while True:
                    if time.time()-start_time > time_limit and enforce_time:
                        break

                    self.screen_processor.update_image()
                    player_pos = self.screen_processor.find_player_minimap_marker()
                    self.update(player_pos[0], player_pos[1])

                    if player_pos[0] >= goal_x - glide_goal_offset:
                        # I've set an explicit offset of 2 pixels but it needs adjustments by trial
                        print("reached goal")
                        break

                self.key_mgr.direct_release(DIK_RIGHT)
                self.key_mgr.direct_release(self.jump_key)

        elif loc_delta > 0:
            # we need to move left
            time_limit = math.ceil(abs_loc_delta / self.x_movement_enforce_rate) + 1
            if ledge:
                self.key_mgr.single_press(DIK_LEFT, 0.1)
                while True:
                    if time.time() - start_time > time_limit and enforce_time:
                        break
                    self.key_mgr.single_press(self.keymap["demon_strike"])
                    self.screen_processor.update_image()
                    player_pos = self.screen_processor.find_player_minimap_marker()
                    self.update(player_pos[0], player_pos[1])
                    if player_pos[0] <= goal_x:
                        return 0  # We can just exit function since we demon strike stops on ledges
            if abs_loc_delta <= glide_threshold:
                # Just walk if distance is less than 10 pixels
                self.key_mgr.direct_press(DIK_LEFT)

                # Below: use a loop to continuously press right until goal is reached or time is up
                while True:
                    if time.time() - start_time > time_limit and enforce_time:
                        break
                    self.screen_processor.update_image()
                    player_pos = self.screen_processor.find_player_minimap_marker()
                    self.update(player_pos[0], player_pos[1])
                    # Problem with synchronizing player_pos with self.x and self.y. Needs to get resolved.
                    # Current solution: Just call self.update() (not good for redundancy)
                    if player_pos[0] <= goal_x + walk_goal_offset:
                        # Reached or exceeded destination x coordinates
                        break

                self.key_mgr.direct_release(DIK_LEFT)

            else:
                # Distance is quite big, so we glide
                # Note: Even if we release keys and stop gliding, MS keeps the character's momentum, so we need to stop prematurely
                self.key_mgr.direct_press(DIK_LEFT)
                self.key_mgr.single_press(self.jump_key, 0.3)
                self.key_mgr.direct_press(self.jump_key)
                while True:
                    if time.time() - start_time > time_limit and enforce_time:
                        break

                    self.screen_processor.update_image()
                    player_pos = self.screen_processor.find_player_minimap_marker()
                    self.update(player_pos[0], player_pos[1])

                    if player_pos[0] <= goal_x + glide_goal_offset:
                        # I've set an explicit offset of 2 pixels but it needs adjustments by trial
                        break

                self.key_mgr.direct_release(DIK_LEFT)
                self.key_mgr.direct_release(self.jump_key)

    def horizontal_move_goal(self, goal_x):
        """
        Blocking call to move from current x position(self.x) to goal_x. Only counts x coordinates.
        Refactor notes: This function references self.screen_processor
        :param goal_x: goal x coordinates
        :return: None
        """
        current_x = self.x
        if goal_x - current_x > 0:
            # need to go right:
            mode = "r"
        elif goal_x - current_x < 0:
            # need to go left:
            mode = "l"
        else:
            return 0

        if mode == "r":
            # need to go right:
            self.key_mgr.direct_press(DIK_RIGHT)
        elif mode == "l":
            # need to go left:
            self.key_mgr.direct_press(DIK_LEFT)
        while True:
            self.update(self.screen_processor.find_player_minimap_marker())
            if not self.x:
                assert 1 == 0, "horizontal_move goal: failed to recognize coordinates"

            if mode == "r":
                if self.x >= goal_x-self.horizontal_goal_offset:
                    self.key_mgr.direct_release(DIK_RIGHT)
                    break
            elif mode == "l":
                if self.x <= goal_x+self.horizontal_goal_offset:
                    self.key_mgr.direct_release(DIK_LEFT)
                    break
        self.key_mgr.reset()

    def dbljump_max(self):
        """Warining: is a blocking call"""
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_release(DIK_ALT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr.direct_release(DIK_UP)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr.direct_release(DIK_UP)

    def dbljump_half(self):
        """Warining: is a blocking call"""
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_release(DIK_ALT)
        time.sleep(0.23)
        self.key_mgr.direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr.direct_release(DIK_UP)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr.direct_release(DIK_UP)

    def jumpl(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_release(DIK_LEFT)
        self.key_mgr.direct_release(DIK_ALT)

    def jumpl_double(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.05)
        self.key_mgr.direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr.direct_release(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr.direct_release(DIK_LEFT)

    def jumpl_glide(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.15)
        self.key_mgr.direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.2)
        self.key_mgr.direct_release(DIK_ALT)
        self.key_mgr.direct_release(DIK_LEFT)

    def jumpr(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_release(DIK_RIGHT)
        self.key_mgr.direct_release(DIK_ALT)

    def jumpr_double(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.05)
        self.key_mgr.direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr.direct_release(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr.direct_release(DIK_RIGHT)


    def jumpr_glide(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.15)
        self.key_mgr.direct_release(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.2)
        self.key_mgr.direct_release(DIK_ALT)
        self.key_mgr.direct_release(DIK_RIGHT)

    def drop(self):
        """Blocking call"""
        self.key_mgr.direct_press(DIK_DOWN)
        time.sleep(0.1)
        self.key_mgr.direct_press(DIK_ALT)
        time.sleep(0.1)
        self.key_mgr.direct_release(DIK_DOWN)
        self.key_mgr.direct_release(DIK_ALT)

    def update(self, player_coords_x, player_coords_y):
        """
        Updates self.x, self.y to input coordinates
        :param player_coords_x: Coordinates to update self.x
        :param player_coords_y: Coordinates to update self.y
        :return: None
        """
        self.x, self.y = player_coords_x, player_coords_y


