import terrain_analyzer as ta
from terrain_analyzer import METHOD_DROP, METHOD_MOVEL, METHOD_MOVER, METHOD_DBLJMP, METHOD_DBLJMP_HALF, METHOD_DBLJMP_MAX
import directinput_constants as dc
import macro_script
import logging, math, time, random

class CustomLogger:
    def __init__(self, logger_obj, logger_queue):
        self.logger_obj = logger_obj
        self.logger_queue = logger_queue

    def debug(self, *args):
        self.logger_obj.debug(" ".join([str(x) for x in args]))
        if self.logger_queue:
            self.logger_queue.put(("log", " ".join([str(x) for x in args])))

    def exception(self, *args):
        self.logger_obj.exception(" ".join([str(x) for x in args]))
        if self.logger_queue:
            self.logger_queue.put(("log", " ".join([str(x) for x in args])))

class MacroControllerAStar(macro_script.MacroController):
    """
    This is a new port of MacroController from macro_script with improved pathing. MacroController Used PlatforScan,
    which is an tree search algorithm I implemented, and works at indivisual platform level. However, V2 uses A* path
    finding and works at pixel level, which allows more randomized and fluent moving.
    """
    def loop(self):
        """
        Main event loop for Macro
        Will now use current coordinates and A* to find a new path.
        :return: loop exit code(same as macro_script.py)
        """
        random.seed((time.time() * 10**4) % 10 **3)

        if not self.player_manager.skill_counter_time:
            self.player_manager.skill_counter_time = time.time()
        if time.time() - self.player_manager.skill_counter_time > 60:
            print("skills casted in duration %d: %d skill/s: %f"%(int(time.time() - self.player_manager.skill_counter_time), self.player_manager.skill_cast_counter, self.player_manager.skill_cast_counter/int(time.time() - self.player_manager.skill_counter_time)))
            self.logger.debug("skills casted in duration %d: %d skill/s: %f skill/s"%(int(time.time() - self.player_manager.skill_counter_time), self.player_manager.skill_cast_counter, self.player_manager.skill_cast_counter/int(time.time() - self.player_manager.skill_counter_time)))
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
            return -1
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
                self.unstick_attempts += 1
                self.unstick()
            if self.unstick_attempts >= self.unstick_attempts_threshold:
                self.logger.debug("unstick() threshold reached. sending error code..")
                return -2
            else:
                return 0
        else:
            self.platform_fail_loops = 0
            self.unstick_attempts = 0
            self.current_platform_hash = get_current_platform

        # Rune Detector
        self.player_manager.update()
        rune_platform_hash, rune_coords = self.find_rune_platform()
        if rune_platform_hash:
            self.logger.debug("need to solve rune at platform {0}".format(rune_platform_hash))
            rune_solve_time_offset = (time.time() - self.player_manager.last_rune_solve_time)
            if rune_solve_time_offset >= self.player_manager.rune_cooldown or rune_solve_time_offset <= 30:
                self.navigate_to_rune_platform()
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
                time.sleep(0.5)
        # End Rune Detector

        # Start inter-platform movement
        dest_platform_hash = random.choice([key for key in self.terrain_analyzer.platforms.keys() if key != self.current_platform_hash])
        dest_platform = self.terrain_analyzer.platforms[dest_platform_hash]
        self.player_manager.update()
        random_platform_coord = (random.randint(dest_platform.start_x, dest_platform.end_x), dest_platform.start_y)
        # Once we have selected the platform to move, we can generate a path using A*
        pathlist = self.terrain_analyzer.astar_pathfind((self.player_manager.x, self.player_manager.y), random_platform_coord)
        print(pathlist)
        for mid_coord, method in pathlist:
            self.player_manager.update()
            print(mid_coord, method)
            if method == METHOD_MOVER or method == METHOD_MOVEL:
                self.player_manager.optimized_horizontal_move(mid_coord[0])
            elif method == METHOD_DBLJMP:
                interdelay = self.terrain_analyzer.calculate_vertical_doublejump_delay(self.player_manager.y, mid_coord[1])
                print(interdelay)
                self.player_manager.dbljump_timed(interdelay)
            elif method == METHOD_DROP:
                self.player_manager.drop()
            time.sleep(1)
        # End inter-platform movement

        self.player_manager.randomize_skill()

        # Other buffs
        self.player_manager.holy_symbol()
        self.player_manager.hyper_body()
        self.player_manager.release_overload()
        time.sleep(0.05)

        # Finished
        self.loop_count += 1
        return 0


    def navigate_to_rune_platform(self):
        """
        Uses A* pathfinding to navigate to rune coord
        :return: None
        """
        pass