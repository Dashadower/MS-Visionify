import keystate_manager as km
import player_controller as pc
import screen_processor as sp
import terrain_analyzer as ta
import rune_solver as rs
import logging, math, time, random, sys

class MacroController:
    def __init__(self, keymap=km.DEFAULT_KEY_MAP):

        #sys.excepthook = self.exception_hook

        self.screen_capturer = sp.MapleScreenCapturer()
        self.logger = logging.getLogger("MacroController")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler("logging.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.debug("MacroController init")
        self.screen_processor = sp.StaticImageProcessor(self.screen_capturer)
        self.terrain_analyzer = ta.PathAnalyzer()
        self.keyhandler = km.KeyboardInputManager()
        self.player_manager = pc.PlayerController(self.keyhandler, self.screen_processor, keymap)


        self.last_platform_hash = None
        self.current_platform_hash = None
        self.goal_platform_hash = None

        self.platform_error = 3  # If y value is same as a platform and within 3 pixels of platform border, consider to be on said platform

        self.rune_model_path = r"arrow_classifier_keras_gray.h5"
        self.rune_solver = rs.RuneDetector(self.rune_model_path, screen_capturer=self.screen_capturer, key_mgr=self.keyhandler)

        self.loop_count = 0  # How many loops did we loop over?
        self.reset_navmap_loop_count = 10  # every x times reset navigation map, scrambling pathing
        self.navmap_reset_type = 1  # navigation map reset type. 1 for random, -1 for just reset
        # Initialization code for self.randomize_skill
        self.thousand_sword_percent = 30
        self.shield_chase_percent = 2
        self.choices = []

        for obj in range(self.thousand_sword_percent):
            self.choices.append(1)
        for obj in range(self.shield_chase_percent):
            self.choices.append(2)

        for obj in range(100-len(self.choices)):
            self.choices.append(0)
        self.logger.debug("MacroController init finished")
    def load_and_process_platform_map(self, path):
        self.terrain_analyzer.load(path)
        self.terrain_analyzer.calculate_navigation_map()
        self.logger.debug("Loaded platform data %s"%(path))

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
            self.logger.debug("Failed to get MS screen rect")
            self.abort()
            return -1

        # Update Screen
        self.screen_processor.update_image(set_focus=False)

        # Update Constants
        player_minimap_pos = self.screen_processor.find_player_minimap_marker()
        if not player_minimap_pos:
            return -2
        self.player_manager.update(player_minimap_pos[0], player_minimap_pos[1])



        # Placeholder for Lie Detector Detector (sounds weird)

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

        if self.loop_count % self.reset_navmap_loop_count == 0 and self.loop_count != 0:
            # Reset navigation map to randomize pathing
            self.terrain_analyzer.calculate_navigation_map()
            numbers = []
            for x in range(0, len(self.terrain_analyzer.platforms.keys())):
                numbers.append(x)
            random.shuffle(numbers)
            idx = 0
            if self.navmap_reset_type == 1:
                for key, platform in self.terrain_analyzer.platforms.items():
                    platform.last_visit = numbers[idx]
                    idx += 1

            self.navmap_reset_type *= -1
            self.logger.debug("navigation map reset and randomized at loop #%d"%(self.loop_count))

        # Placeholder for Rune Detector
        rune_coords = self.screen_processor.find_rune_marker()
        if rune_coords:
            self.logger.debug("need to solve rune at {0}".format(rune_coords))
            rune_solve_time_offset = (time.time() - self.player_manager.last_rune_solve_time)
            if rune_solve_time_offset >= self.player_manager.rune_cooldown or rune_solve_time_offset <= 15:
                rune_platform_hash = None
                for key, platform in self.terrain_analyzer.platforms.items():
                    if rune_coords[1] >= platform.start_y - 1 and \
                            rune_coords[1] <= platform.start_y + 1 and \
                            rune_coords[0] >= platform.start_x and \
                            rune_coords[0] <= platform.end_x:
                        rune_platform_hash = key
                for key, platform in self.terrain_analyzer.oneway_platforms.items():
                    if rune_coords[1] >= platform.start_y - 1 and \
                            rune_coords[1] <= platform.start_y + 1 and \
                            rune_coords[0] >= platform.start_x and \
                            rune_coords[0] <= platform.end_x:
                        rune_platform_hash = key

                if rune_platform_hash:
                    rune_solutions = self.terrain_analyzer.pathfind(self.current_platform_hash, rune_platform_hash)
                    if rune_solutions:
                        for solution in rune_solutions:
                            if self.player_manager.x < solution.lower_bound[0]:
                                # We are left of solution bounds.
                                # print("run sweep move")
                                self.player_manager.horizontal_move_goal(solution.lower_bound[0])

                            else:
                                # We are right of solution bounds
                                # print("run sweep move")
                                self.player_manager.horizontal_move_goal(solution.upper_bound[0])
                            time.sleep(1)
                            rune_movement_type = solution.method
                            if rune_movement_type == ta.METHOD_DROP:
                                self.player_manager.drop()
                                time.sleep(1)
                            elif rune_movement_type == ta.METHOD_JUMPL:
                                self.player_manager.jumpl_double()
                                time.sleep(0.5)
                            elif rune_movement_type == ta.METHOD_JUMPR:
                                self.player_manager.jumpr_double()
                                time.sleep(0.5)
                            elif rune_movement_type == ta.METHOD_DBLJMP_MAX:
                                self.player_manager.dbljump_max()
                                time.sleep(1)
                            elif rune_movement_type == ta.METHOD_DBLJMP_HALF:
                                self.player_manager.dbljump_half()
                                time.sleep(1)

                        time.sleep(0.5)

                    self.player_manager.update()
                    if self.player_manager.x < rune_coords[0]-1 or self.player_manager.x > rune_coords[0]+1:
                        self.player_manager.horizontal_move_goal(rune_coords[0])

                    time.sleep(1)
                    self.rune_solver.press_space()
                    self.rune_solver.solve_auto()
                    time.sleep(2)
                    self.player_manager.last_rune_solve_time = time.time()

        # End Placeholder


        # We are on a platform. find an optimal way to clear platform.
        # If we know our next platform destination, we can make our path even more efficient
        next_platform_solution = self.terrain_analyzer.select_move(self.current_platform_hash)
        #print("next platform solution:", next_platform_solution.method, next_platform_solution.to_hash)
        self.logger.debug("next solution destination: %s"%(next_platform_solution.to_hash))
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

        self.randomize_skill()

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

        time.sleep(0.1)

        # All movement and attacks finished. Now perform movement
        movement_type = next_platform_solution.method
        #self.player_manager.shield_chase()

        #print("actuating movement...", movement_type)

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
        time.sleep(0.05)
        # Finished
        self.loop_count += 1
        return 0

    def abort(self):
        self.logger.debug("aborted")
        self.keyhandler.reset()

    def randomize_skill(self):
        selection = random.choice(self.choices)
        if selection == 0:
            return 0
        elif selection == 1:
            self.player_manager.thousand_sword()
        elif selection == 2:
            self.player_manager.shield_chase()


