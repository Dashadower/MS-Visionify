import keystate_manager as km
import player_controller as pc
import screen_processor as sp
import terrain_analyzer as ta
import directinput_constants as dc
import rune_solver as rs
import logging, math, time, random, sys

class CustomLogger:
    def __init__(self, logger_obj, logger_queue):
        self.logger_obj = logger_obj
        self.logger_queue = logger_queue

    def debug(self, *args):
        self.logger_obj.debug(" ".join([str(x) for x in args]))
        self.logger_queue.put(("log", " ".join([str(x) for x in args])))

    def exception(self, *args):
        self.logger_obj.exception(" ".join([str(x) for x in args]))
        self.logger_queue.put(("log", " ".join([str(x) for x in args])))

class MacroControllerV2:
    """
    This is a new port of MacroController from macro_script with improved pathing. MacroController Used PlatforScan,
    which is an tree search algorithm I implemented, and works at indivisual platform level. However, V2 uses A* path
    finding and works at pixel level, which allows more randomized and fluent moving.
    """
    def __init__(self, keymap=km.DEFAULT_KEY_MAP, log_queue=None):

        #sys.excepthook = self.exception_hook

        self.screen_capturer = sp.MapleScreenCapturer()
        logger = logging.getLogger("MacroControllerV2")
        logger.setLevel(logging.DEBUG)
        self.log_queue = log_queue
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler("logging.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.logger = CustomLogger(logger, self.log_queue)
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
        self.rune_platform_offset = 2

        self.loop_count = 0  # How many loops did we loop over?
        self.reset_navmap_loop_count = 10  # every x times reset navigation map, scrambling pathing
        self.navmap_reset_type = 1  # navigation map reset type. 1 for random, -1 for just reset. GETS ALTERNATED

        self.walk_probability = 5
        # This sets random.randint(1, walk_probability) to decide of moonlight slash should just walk instead of glide
        # Probability of walking is (1/walk_probability) * 100

        self.restrict_moonlight_slash_probability = 5

        self.platform_fail_loops = 0
        # How many loops passed and we are not on a platform?

        self.platform_fail_loop_threshold = 10
        # If self.platform_fail_loops is greater than threshold, run unstick()

        self.logger.debug("MacroController init finished")

    def load_and_process_platform_map(self, path):
        self.terrain_analyzer.load(path)
        self.terrain_analyzer.generate_solution_dict()
        self.logger.debug("Loaded platform data %s"%(path))

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def find_current_platform(self):
        current_platform_hash = None

        for key, platform in self.terrain_analyzer.oneway_platforms.items():
            if self.player_manager.y >= min(platform.start_y, platform.end_y) and \
                    self.player_manager.y <= max(platform.start_y, platform.end_y) and \
                    self.player_manager.x >= platform.start_x and \
                    self.player_manager.x <= platform.end_x:
                current_platform_hash = platform.hash
                break

        for key, platform in self.terrain_analyzer.platforms.items():
            if self.player_manager.y == platform.start_y and \
                    self.player_manager.x >= platform.start_x and \
                    self.player_manager.x <= platform.end_x:
                current_platform_hash = platform.hash
                break

        #  Add additional check to take into account imperfect platform coordinates
        for key, platform in self.terrain_analyzer.platforms.items():
            if self.player_manager.y == platform.start_y and \
                    self.player_manager.x >= platform.start_x - self.platform_error and \
                    self.player_manager.x <= platform.end_x + self.platform_error:
                current_platform_hash = platform.hash
                break

        if current_platform_hash:
            return current_platform_hash
        else:
            return 0

    def loop(self):
        """
        Main event loop for Macro
        Will now use current coordinates and A* to find a new path.
        :return: loop exit code
        """
        # Check if MapleStory window is alive
        random.seed((time.time() * 10**4) % 10 **3)
        if random.randint(1, self.restrict_moonlight_slash_probability) == 2:
            restrict_moonlight_slash = True
        else:
            restrict_moonlight_slash = False

        if not self.player_manager.skill_counter_time:
            self.player_manager.skill_counter_time = time.time()
        if time.time() - self.player_manager.skill_counter_time > 60:
            print("skills casted in duration %d: %d skill/s: %f"%(int(time.time() - self.player_manager.skill_counter_time), self.player_manager.skill_cast_counter, self.player_manager.skill_cast_counter/int(time.time() - self.player_manager.skill_counter_time)))
            self.logger.debug("skills casted in duration %d: %d skill/s: %f"%(int(time.time() - self.player_manager.skill_counter_time), self.player_manager.skill_cast_counter, self.player_manager.skill_cast_counter/int(time.time() - self.player_manager.skill_counter_time)))
            self.player_manager.skill_cast_counter = 0
            self.player_manager.skill_counter_time = time.time()
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
        get_current_platform = self.find_current_platform()
        if not get_current_platform:
            # Move to nearest platform and redo loop
            # Failed to find platform.
            self.platform_fail_loops += 1
            if self.platform_fail_loops >= self.platform_fail_loop_threshold:
                self.logger.debug("stuck. attempting unstick()...")
                self.unstick()
            return -1
        else:
            self.platform_fail_loops = 0
            self.current_platform_hash = get_current_platform


        # Placeholder for Rune Detector
        self.player_manager.update()
        rune_coords = self.screen_processor.find_rune_marker()
        if rune_coords:
            self.logger.debug("need to solve rune at {0}".format(rune_coords))
            rune_solve_time_offset = (time.time() - self.player_manager.last_rune_solve_time)
            if rune_solve_time_offset >= self.player_manager.rune_cooldown or rune_solve_time_offset <= 30:
                rune_platform_hash = None
                for key, platform in self.terrain_analyzer.platforms.items():
                    if rune_coords[1] >= platform.start_y - self.rune_platform_offset and \
                            rune_coords[1] <= platform.start_y + self.rune_platform_offset and \
                            rune_coords[0] >= platform.start_x and \
                            rune_coords[0] <= platform.end_x:
                        rune_platform_hash = key
                for key, platform in self.terrain_analyzer.oneway_platforms.items():
                    if rune_coords[1] >= platform.start_y - self.rune_platform_offset and \
                            rune_coords[1] <= platform.start_y + self.rune_platform_offset and \
                            rune_coords[0] >= platform.start_x and \
                            rune_coords[0] <= platform.end_x:
                        rune_platform_hash = key

                if rune_platform_hash:
                    self.logger.debug("rune on platform %s"%(rune_platform_hash))
                    if self.current_platform_hash != rune_platform_hash:
                        rune_solutions = self.terrain_analyzer.pathfind(self.current_platform_hash, rune_platform_hash)
                        if rune_solutions:
                            self.logger.debug("paths to rune: %s" % (" ".join(x.method for x in rune_solutions)))
                            print(" ".join(x.method for x in rune_solutions))
                            for solution in rune_solutions:
                                if self.player_manager.x < solution.lower_bound[0]:
                                    # We are left of solution bounds.
                                    self.player_manager.horizontal_move_goal(solution.lower_bound[0])
                                else:
                                    # We are right of solution bounds
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
                    time.sleep(1.5)
                    solve_result = self.rune_solver.solve_auto()
                    self.logger.debug("rune_solver.solve_auto results: %d" % (solve_result))
                    if solve_result == -1:
                        self.logger.debug("rune_solver.solve_auto failed to solve")
                        for x in range(4):
                            self.keyhandler.single_press(dc.DIK_LEFT)

                    self.player_manager.last_rune_solve_time = time.time()
                    self.current_platform_hash = rune_platform_hash
                    time.sleep(1)

        # End Placeholder



        #End inter-platform movement

        # Other buffs
        self.player_manager.holy_symbol()
        self.player_manager.hyper_body()
        self.player_manager.release_overload()
        time.sleep(0.05)

        # Finished
        self.loop_count += 1
        return 0


    def unstick(self):
        """
        Run when script can't find which platform we are at.
        Solution: try random stuff to attempt it to reposition it self
        :return: None
        """
        #Method one: get off ladder
        self.player_manager.jumpr()
        time.sleep(2)
        if self.find_current_platform():
            return 0
        self.player_manager.dbljump_max()
        time.sleep(2)
        if self.find_current_platform():
            return 0


    def abort(self):
        self.logger.debug("aborted")
        if self.log_queue:
            self.log_queue.put(["stopped", None])
        self.keyhandler.reset()



