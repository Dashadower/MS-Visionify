import keystate_manager as km
import player_controller as pc
import screen_processor as sp
import terrain_analyzer as ta
import queue, math, time, random


class MacroController:
    def __init__(self, keymap=km.DEFAULT_KEY_MAP):
        self.screen_capturer = sp.MapleScreenCapturer()
        self.screen_processor = sp.StaticImageProcessor(self.screen_capturer)
        self.terrain_analyzer = ta.PathAnalyzer()
        self.keyhandler = km.KeyboardInputManager()
        self.player_manager = pc.PlayerController(self.keyhandler, self.screen_processor, keymap)

        self.last_platform_hash = None
        self.current_platform_hash = None
        self.goal_platform_hash = None

        self.platform_error = 3  # If y value is same as a platform and within 3 pixels of platform border, consider to be on said platform

        # Initialization code for self.randomize_skill
        self.thousand_sword_percent = 30
        self.shield_chase_percent = 30
        self.choices = []

        for obj in range(self.thousand_sword_percent):
            self.choices.append(1)
        for obj in range(self.shield_chase_percent):
            self.choices.append(2)

        for obj in range(100-len(self.choices)):
            self.choices.append(0)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def loop(self):
        """
        Main event loop for Macro
        Important note: Since this function uses PathAnalyzer's pathing algorithm, when this function moves to a new
        platform, it will invoke PathAnalyzer.move_platform. HOWEVER, in an attempt to make the system error-proof,
        platform movement and solution flagging is done on the loop call succeeding the loop call where the actual
        move ment is made. self.goal_platform is used for such purpose.
        :return: loop exit code
        """
        # Check if MapleStory window is alive
        if not self.screen_capturer.ms_get_screen_hwnd():
            self.abort()
            return -1

        # Update Screen
        self.screen_processor.update_image()

        # Update Constants
        player_minimap_pos = self.screen_processor.find_player_minimap_marker()
        if not player_minimap_pos:
            return -2
        self.player_manager.update(player_minimap_pos[0], player_minimap_pos[1])

        self.randomize_skill()

        # Placeholder for Lie Detector Detector (sounds weird)

        # End Placeholder

        # Placeholder for Rune Detector

        # End Placeholder

        # Check if player is on platform
        self.current_platform_hash = None
        oneway = False
        for key, platform in self.terrain_analyzer.oneway_platforms.items():
            if self.player_manager.y >= min(platform.start_y, platform.end_y) and \
                self.player_manager.y <= max(platform.start_y, platform.end_y) and \
                self.player_manager.x >= platform.start_x and \
                self.player_manager.x <= platform.end_x:
                self.current_platform_hash = platform.hash
                oneway = True
                break

        for key, platform in self.terrain_analyzer.platforms.items():
            if self.player_manager.y == platform.start_y and \
                self.player_manager.x >= platform.start_x and \
                self.player_manager.x <= platform.end_x:
                self.current_platform_hash = platform.hash
                break

        #  Add additional check to take into account imperfect platform coordinates
        for key, platform in self.terrain_analyzer.platforms.items():
            if self.player_manager.y == platform.start_y and \
                    self.player_manager.x >= platform.start_x - self.platform_error and \
                    self.player_manager.x <= platform.end_x + self.platform_error:
                self.current_platform_hash = platform.hash
                break



        if not self.current_platform_hash:
            # Move to nearest platform and redo loop
            # Failed to find platform.

            return -1

        # Update navigation dictionary with last_platform and current_platform
        if self.goal_platform_hash and self.current_platform_hash == self.goal_platform_hash:
            self.terrain_analyzer.move_platform(self.last_platform_hash, self.current_platform_hash)

        # Reinitialize last_platform to current_platform
        self.last_platform_hash = self.current_platform_hash

        # We are on a platform. find an optimal way to clear platform.
        # If we know our next platform destination, we can make our path even more efficient
        next_platform_solution = self.terrain_analyzer.select_move(self.current_platform_hash)
        print("next platform solution:", next_platform_solution.method, next_platform_solution.to_hash)

        self.goal_platform_hash = next_platform_solution.to_hash


        # lookahead pathing
        lookahead_platform_solution = self.terrain_analyzer.select_move(self.goal_platform_hash)
        lookahead_solution_lb = lookahead_platform_solution.lower_bound
        lookahead_solution_ub = lookahead_platform_solution.upper_bound

        #lookahead_lb = lookahead_lb[0] if lookahead_lb[0] >= next_platform_solution.lower_bound[0] else next_platform_solution.lower_bound[0]
        #lookahead_ub = lookahead_ub[0] if lookahead_ub[0] <= next_platform_solution.upper_bound[0] else next_platform_solution.upper_bound[0]

        if lookahead_solution_lb[0] < next_platform_solution.lower_bound[0] and lookahead_solution_ub[0] > next_platform_solution.lower_bound[0] or \
                lookahead_solution_lb[0] > next_platform_solution.lower_bound[0] and lookahead_solution_lb[0] < next_platform_solution.upper_bound[0]:
            lookahead_lb = lookahead_solution_lb[0] if lookahead_solution_lb[0] >= next_platform_solution.lower_bound[0] and lookahead_solution_lb[0] <= next_platform_solution.upper_bound[0] else next_platform_solution.lower_bound[0]
            lookahead_ub = lookahead_solution_ub[0] if lookahead_solution_ub[0] <= next_platform_solution.upper_bound[0] and lookahead_solution_ub[0] >= next_platform_solution.lower_bound[0] else next_platform_solution.upper_bound[0]

        else:
            lookahead_lb = next_platform_solution.lower_bound[0]
            lookahead_ub = next_platform_solution.upper_bound[0]


        # Find the closest location to next_platform_solution
        if self.player_manager.x >= next_platform_solution.lower_bound[0] and self.player_manager.x <= next_platform_solution.upper_bound[0]:
            # We are within the solution bounds. attack within solution range and move
            if abs(self.player_manager.x - next_platform_solution.lower_bound[0]) < abs(self.player_manager.x - next_platform_solution.upper_bound[0]):
                # We are closer to lower boound, so move to upper bound to maximize movement
                in_solution_movement_goal = lookahead_ub
            else:
                in_solution_movement_goal = lookahead_lb
            self.player_manager.moonlight_slash_sweep_move(in_solution_movement_goal)

        else:
            # We need to move within the solution bounds. First, find closest solution bound which can cover majority of current platform.
            if self.player_manager.x < next_platform_solution.lower_bound[0]:
                # We are left of solution bounds.
                #print("run sweep move")
                self.player_manager.moonlight_slash_sweep_move(lookahead_ub)

            else:
                # We are right of solution bounds
                #print("run sweep move")
                self.player_manager.moonlight_slash_sweep_move(lookahead_lb)


        time.sleep(0.2)
        # All movement and attacks finished. Now perform movement
        movement_type = next_platform_solution.method
        print("actuating movement...", movement_type)

        if movement_type == ta.METHOD_DROP:
            self.player_manager.drop()
            time.sleep(1)
        elif movement_type == ta.METHOD_JUMPL:
            self.player_manager.jumpl_double()
            time.sleep(0.5)
        elif movement_type == ta.METHOD_JUMPR:
            self.player_manager.jumpr_double()
            time.sleep(0.5)
        elif movement_type == ta.METHOD_DBLJMP_MAX:
            self.player_manager.dbljump_max()
            time.sleep(1)
        elif movement_type == ta.METHOD_DBLJMP_HALF:
            self.player_manager.dbljump_half()
            time.sleep(1)


        self.player_manager.release_overload()
        time.sleep(0.1)
        # Finished
        return 0


    def abort(self):
        pass

    def randomize_skill(self):
        selection = random.choice(self.choices)
        if selection == 0:
            return 0
        elif selection == 1:
            self.player_manager.thousand_sword()
        elif selection == 2:
            self.player_manager.shield_chase()


