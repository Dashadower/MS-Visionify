from directinput_constants import DIK_RIGHT, DIK_DOWN, DIK_LEFT, DIK_UP, DIK_ALT
from keystate_manager import DEFAULT_KEY_MAP
import time, math, random
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

        Bot States:
        Idle
        ChangePlatform
        AttackinPlatform
        """
        self.x = None
        self.y = None


        self.keymap = {}
        for key, value in keymap.items():
            self.keymap[key] = value[0]
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

        self.x_movement_enforce_rate = 15  # refer to optimized_horizontal_move

        self.moonlight_slash_x_radius = 13  # exceed: moonlight slash's estimalte x hitbox RADIUS in minimap coords.
        self.moonlight_slash_delay = 1.0 * 0.45  # delay after using MS where character is not movable

        self.horizontal_movement_threshold = 21 # Glide instead of walk if distance greater than threshold

        self.skill_cast_counter = 0
        self.skill_counter_time = 0

        self.last_shield_chase_time = 0
        self.shield_chase_cooldown = 6
        self.shield_chase_delay = 1.0  # delay after using SC where character is not movable
        self.last_shield_chase_coords = None
        self.min_shield_chase_distance = 20

        self.last_thousand_sword_time = 0
        self.thousand_sword_cooldown = 8 + 2
        self.thousand_sword_delay = 1.6  # delay after using thousand sword where character is not movable
        self.last_thousand_sword_coords = None
        self.min_thousand_sword_distance = 25

        self.rune_cooldown = 60 * 15  # 15 minutes for rune cooldown
        self.last_rune_solve_time = 0

        self.holy_symbol_cooldown = 60 * 3 + 1
        self.last_holy_symbol_time = 0
        self.holy_symbol_delay = 1.7

        self.overload_stack = 0

        # Initialization code for self.randomize_skill
        self.thousand_sword_percent = 30
        self.shield_chase_percent = 40
        self.choices = []

        for obj in range(self.thousand_sword_percent):
            self.choices.append(1)
        for obj in range(self.shield_chase_percent):
            self.choices.append(2)

        for obj in range(100 - len(self.choices)):
            self.choices.append(0)

    def update(self, player_coords_x=None, player_coords_y=None):
        """
        Updates self.x, self.y to input coordinates
        :param player_coords_x: Coordinates to update self.x
        :param player_coords_y: Coordinates to update self.y
        :return: None
        """
        if not player_coords_x:
            self.screen_processor.update_image()
            scrp_ret_val = self.screen_processor.find_player_minimap_marker()
            if scrp_ret_val:
                player_coords_x, player_coords_y = scrp_ret_val
            else:
                #raise Exception("screen_processor did not return coordinates!!")
                player_coords_x = self.x
                player_coords_y = self.y
        self.x, self.y = player_coords_x, player_coords_y

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

    def distance(self, coord1, coord2):
        return math.sqrt((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)

    def moonlight_slash_sweep_move(self, goal_x, glide=True, no_attack_distance=0):
        """
        This function will, while moving towards goal_x, constantly use exceed: moonlight slash and not overlapping
        This function currently does not have an time enforce implementation, meaning it may fall into an infinite loop
        if player coordinates are not read correctly.
        X coordinate max error on flat surface: +- 5 pixels
        :param goal_x: minimap x goal coordinate.
        :param glide: If True, will used optimized_horizontal_move. Else, will use horizontal_move_goal
        :param no_attack_distance: Distance in x pixels where any attack skill would not be used and just move
        :return: None
        """
        start_x = self.x
        loc_delta = self.x - goal_x
        abs_loc_delta = abs(loc_delta)

        time.sleep(abs(self.random_duration()))
        if not no_attack_distance:
            self.moonlight_slash()
            time.sleep(abs(self.random_duration()))
        if loc_delta > 0:
            # left movement
            if no_attack_distance and no_attack_distance < abs_loc_delta:
                self.optimized_horizontal_move(self.x-no_attack_distance+self.horizontal_goal_offset)

            self.update()
            loc_delta = self.x - goal_x
            abs_loc_delta = abs(loc_delta)
            if abs_loc_delta < self.moonlight_slash_x_radius:
                self.horizontal_move_goal(goal_x)

            else:
                while True:
                    self.update()

                    if self.x <= goal_x + self.horizontal_goal_offset:
                        break

                    elif abs(self.x - goal_x) < self.moonlight_slash_x_radius * 2:
                        #  Movement distance is too short to effectively glide. So just wak
                        if glide:
                            self.optimized_horizontal_move(goal_x)
                        else:
                            self.horizontal_move_goal(goal_x)
                        time.sleep(0.1)
                        if abs(self.x - start_x) >= no_attack_distance:
                            time.sleep(abs(self.random_duration()))
                            self.moonlight_slash()
                            time.sleep(abs(self.random_duration()))
                            self.randomize_skill()
                        time.sleep(abs(self.random_duration(0.7)))

                    else:
                        if glide:
                            self.optimized_horizontal_move(self.x - self.moonlight_slash_x_radius * 2 + self.random_duration(2, 0))
                        else:
                            self.horizontal_move_goal(self.x - self.moonlight_slash_x_radius * 2 + self.random_duration(2, 0))
                        time.sleep(0.1)
                        time.sleep(abs(self.random_duration()))
                        self.moonlight_slash()
                        time.sleep(abs(self.random_duration()))
                        self.randomize_skill()
                        time.sleep(abs(self.random_duration(0.7)))

        elif loc_delta < 0:
            # right movement
            if no_attack_distance and no_attack_distance < abs_loc_delta:
                self.optimized_horizontal_move(self.x+no_attack_distance-self.horizontal_goal_offset)
            self.update()
            loc_delta = self.x - goal_x
            abs_loc_delta = abs(loc_delta)
            if abs_loc_delta < self.moonlight_slash_x_radius:
                self.horizontal_move_goal(goal_x)

            else:
                while True:
                    self.update()

                    if self.x >= goal_x - self.horizontal_goal_offset:
                        break

                    elif abs(goal_x - self.x) < self.moonlight_slash_x_radius * 2:
                        if glide:
                            self.optimized_horizontal_move(goal_x)
                        else:
                            self.horizontal_move_goal(goal_x)
                        time.sleep(0.1)
                        if abs(self.x - start_x) >= no_attack_distance:
                            time.sleep(abs(self.random_duration()))
                            self.moonlight_slash()
                            time.sleep(abs(self.random_duration()))
                            self.randomize_skill()
                            time.sleep(abs(self.random_duration(0.7)))
                    else:
                        if glide:
                            self.optimized_horizontal_move(self.x + self.moonlight_slash_x_radius * 2 - abs(self.random_duration(2, 0)))
                        else:
                            self.horizontal_move_goal(self.x + self.moonlight_slash_x_radius * 2 - abs(self.random_duration(2, 0)))
                        time.sleep(0.1)
                        time.sleep(abs(self.random_duration()))
                        self.moonlight_slash()
                        time.sleep(abs(self.random_duration()))
                        self.randomize_skill()
                        time.sleep(abs(self.random_duration(0.7)))

    def optimized_horizontal_move(self, goal_x, ledge=False, enforce_time=True):
        """
        Move from self.x to goal_x in as little time as possible. Uses multiple movement solutions for efficient paths. Blocking call
        :param goal_x: x coordinate to move to. This function only takes into account x coordinate movements.
        :param ledge: If true, goal_x is an end of a platform, and additional movement solutions can be used. If not, precise movement is required.
        :param enforce_time: If true, the function will stop moving after a time threshold is met and still haven't
        met the goal. Default threshold is 15 minimap pixels per second.
        :return: None
        """
        loc_delta = self.x - goal_x
        abs_loc_delta = abs(loc_delta)
        start_time = time.time()
        horizontal_goal_offset = self.horizontal_goal_offset
        if loc_delta < 0:
            # we need to move right
            time_limit = math.ceil(abs_loc_delta/self.x_movement_enforce_rate)
            if abs_loc_delta <= self.horizontal_movement_threshold:
                # Just walk if distance is less than threshold
                self.key_mgr._direct_press(DIK_RIGHT)

                # Below: use a loop to continously press right until goal is reached or time is up
                while True:
                    if time.time()-start_time > time_limit:
                        break

                    self.update()
                    # Problem with synchonizing player_pos with self.x and self.y. Needs to get resolved.
                    # Current solution: Just call self.update() (not good for redundancy)
                    if self.x >= goal_x - self.horizontal_goal_offset:
                        # Reached or exceeded destination x coordinates
                        break

                self.key_mgr._direct_release(DIK_RIGHT)

            else:
                # Distance is quite big, so we glide
                self.key_mgr._direct_press(DIK_RIGHT)
                time.sleep(abs(0.05+self.random_duration(gen_range=0.1)))
                self.key_mgr._direct_press(self.jump_key)
                time.sleep(abs(0.15+self.random_duration(gen_range=0.15)))
                self.key_mgr._direct_release(self.jump_key)
                time.sleep(abs(0.1+self.random_duration(gen_range=0.15)))
                self.key_mgr._direct_press(self.jump_key)
                while True:
                    if time.time() - start_time > time_limit:
                        break

                    self.update()
                    if self.x >= goal_x - self.horizontal_goal_offset * 3:
                        break
                self.key_mgr._direct_release(self.jump_key)
                time.sleep(0.1 + self.random_duration(gen_range=0.1))
                self.key_mgr._direct_release(DIK_RIGHT)


        elif loc_delta > 0:
            # we are moving to the left
            time_limit = math.ceil(abs_loc_delta / self.x_movement_enforce_rate)
            if abs_loc_delta <= self.horizontal_movement_threshold:
                # Just walk if distance is less than 10
                self.key_mgr._direct_press(DIK_LEFT)

                # Below: use a loop to continously press left until goal is reached or time is up
                while True:
                    if time.time()-start_time > time_limit:
                        break

                    self.update()
                    # Problem with synchonizing player_pos with self.x and self.y. Needs to get resolved.
                    # Current solution: Just call self.update() (not good for redundancy)
                    if self.x <= goal_x + self.horizontal_goal_offset:
                        # Reached or exceeded destination x coordinates
                        break

                self.key_mgr._direct_release(DIK_LEFT)

            else:
                # Distance is quite big, so we glide
                self.key_mgr._direct_press(DIK_LEFT)
                time.sleep(abs(0.05+self.random_duration(gen_range=0.1)))
                self.key_mgr._direct_press(self.jump_key)
                time.sleep(abs(0.15+self.random_duration(gen_range=0.15)))
                self.key_mgr._direct_release(self.jump_key)
                time.sleep(abs(0.1+self.random_duration(gen_range=0.15)))
                self.key_mgr._direct_press(self.jump_key)
                while True:
                    if time.time() - start_time > time_limit:
                        break

                    self.update()
                    if self.x <= goal_x + self.horizontal_goal_offset * 3:
                        break
                self.key_mgr._direct_release(self.jump_key)
                time.sleep(0.1 + self.random_duration(gen_range=0.1))
                self.key_mgr._direct_release(DIK_LEFT)

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
            self.key_mgr._direct_press(DIK_RIGHT)
        elif mode == "l":
            # need to go left:
            self.key_mgr._direct_press(DIK_LEFT)
        while True:
            self.update()
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


    def dbljump_max(self):
        """Warining: is a blocking call"""
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.1 + self.random_duration(0.1))
        self.key_mgr._direct_release(self.jump_key)
        time.sleep(abs(0.05 + self.random_duration(0.1)))
        self.key_mgr._direct_press(DIK_UP)
        time.sleep(abs(0.01 + self.random_duration(0.1)))
        self.key_mgr._direct_release(DIK_UP)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_UP)
        time.sleep(abs(0.01 + self.random_duration(0.1)))
        self.key_mgr._direct_release(DIK_UP)

    def dbljump_half(self):
        """Warining: is a blocking call"""
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.1 + self.random_duration(0.1))
        self.key_mgr._direct_release(self.jump_key)
        time.sleep(0.23 + self.random_duration(0.1))
        self.key_mgr._direct_press(DIK_UP)
        time.sleep(0.01)
        self.key_mgr._direct_release(DIK_UP)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_UP)
        time.sleep(abs(0.01 + self.random_duration(0.15)))
        self.key_mgr._direct_release(DIK_UP)

    def jumpl(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_LEFT)
        self.key_mgr._direct_release(self.jump_key)

    def jumpl_double(self):
        """Blocking call"""
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(abs(0.05 + self.random_duration(0.2)))
        self.key_mgr._direct_release(self.jump_key)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(abs(0.05 + self.random_duration(0.2)))
        self.key_mgr._direct_release(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(abs(0.05 + self.random_duration(0.2)))
        self.key_mgr._direct_release(DIK_LEFT)

    def jumpl_glide(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_LEFT)
        time.sleep(0.05)
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.15)
        self.key_mgr._direct_release(self.jump_key)
        time.sleep(0.1)
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.2)
        self.key_mgr._direct_release(self.jump_key)
        self.key_mgr._direct_release(DIK_LEFT)

    def jumpr(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.1)
        self.key_mgr._direct_release(DIK_RIGHT)
        self.key_mgr._direct_release(self.jump_key)

    def jumpr_double(self):
        """Blocking call"""
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(abs(0.05+self.random_duration(0.2)))
        self.key_mgr._direct_release(self.jump_key)
        time.sleep(0.1)
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(abs(0.05 + self.random_duration(0.2)))
        self.key_mgr._direct_release(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(abs(0.05 + self.random_duration(0.2)))
        self.key_mgr._direct_release(DIK_RIGHT)

    def jumpr_glide(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_RIGHT)
        time.sleep(0.05)
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.15)
        self.key_mgr._direct_release(self.jump_key)
        time.sleep(0.1)
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(0.2)
        self.key_mgr._direct_release(self.jump_key)
        self.key_mgr._direct_release(DIK_RIGHT)

    def drop(self):
        """Blocking call"""
        self.key_mgr._direct_press(DIK_DOWN)
        time.sleep(abs(0.1+self.random_duration()))
        self.key_mgr._direct_press(self.jump_key)
        time.sleep(abs(0.1+self.random_duration()))
        self.key_mgr._direct_release(DIK_DOWN)
        time.sleep(abs(0.1+self.random_duration()))
        self.key_mgr._direct_release(self.jump_key)

    def moonlight_slash(self):

        self.key_mgr.single_press(self.keymap["moonlight_slash"], additional_duration=abs(self.random_duration(0.2)))
        self.overload_stack += 1
        self.skill_cast_counter += 1
        time.sleep(self.moonlight_slash_delay)

    def thousand_sword(self):
        if time.time() - self.last_thousand_sword_time > self.thousand_sword_cooldown:
            self.update()
            if self.distance((self.x, self.y), self.last_thousand_sword_coords if self.last_thousand_sword_coords else (1000,1000)) >= self.min_thousand_sword_distance or \
                    time.time() - self.last_thousand_sword_time > self.thousand_sword_cooldown*3:
                self.key_mgr.single_press(self.keymap["thousand_sword"], additional_duration=abs(self.random_duration()))
                self.last_thousand_sword_time = time.time()
                self.skill_cast_counter += 1
                self.last_thousand_sword_coords = (self.x, self.y)
                self.overload_stack += 5
                print("thousand sword cast")
                time.sleep(self.thousand_sword_delay)

    def shield_chase(self):
        if time.time() - self.last_shield_chase_time > self.shield_chase_cooldown:
            if self.distance((self.x, self.y), self.last_shield_chase_coords if self.last_shield_chase_coords else (1000,1000)) >= self.min_shield_chase_distance or \
                    time.time() - self.last_shield_chase_time > self.shield_chase_cooldown*3:
                count = random.randrange(1, 3)
                self.update()
                cast_yccords = self.y
                for c in range(count):
                    self.key_mgr.single_press(self.keymap["shield_chase"], additional_duration=abs(self.random_duration(gen_range=0.2)))
                self.key_mgr.single_press(DIK_ALT)
                self.update()
                after_cast_ycoords = self.y
                print("shield chase cast")
                if cast_yccords == after_cast_ycoords:
                    #  Shield chase has been used.
                    self.last_shield_chase_time = time.time()
                    self.last_shield_chase_coords = (self.x, self.y)
                    self.skill_cast_counter += 1
                    time.sleep(self.shield_chase_delay - 0.2)
                    print("shield chase cast - actually casted")
                    return 0
                else:
                    # No monsters nearby, was not used
                    print("shield chase cast - not casted")
                    time.sleep(1)
                    return 1

    def holy_symbol(self):
        if time.time() - self.last_holy_symbol_time > self.holy_symbol_cooldown + random.randint(0, 14):
            self.key_mgr.single_press(self.keymap["holy_symbol"], additional_duration=abs(self.random_duration()))
            self.skill_cast_counter += 1
            self.last_holy_symbol_time = time.time()
            time.sleep(self.holy_symbol_delay)

    def release_overload(self):
        if self.overload_stack >= 18 + random.randint(0, 12):
            self.key_mgr.single_press(self.keymap["release_overload"],additional_duration=abs(self.random_duration()))
            self.skill_cast_counter += 1
            self.overload_stack = 0
            time.sleep(0.2)

    def randomize_skill(self):
        selection = random.choice(self.choices)
        if selection == 0:
            return 0
        elif selection == 1:
            self.thousand_sword()
            return 0
        elif selection == 2:
            retval = self.shield_chase()
            if retval == 0:
                return 2
            else:
                return 0

    def random_duration(self, gen_range=0.5, digits=2):
        """
        returns a random number x where -gen_range<=x<=gen_range rounded to digits number of digits under floating points
        :param gen_range: float for generating number x where -gen_range<=x<=gen_range
        :param digits: n digits under floating point to round. 0 returns integer as float type
        :return: random number float
        """
        d = round(random.uniform(0, gen_range), digits)
        if random.choice([1,-1]) == -1:
            d *= -1
        return d
