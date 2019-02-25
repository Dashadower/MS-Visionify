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
            return -2
        self.player_manager.update(player_minimap_pos[0], player_minimap_pos[1])

        # Placeholder for Lie Detector Detector (sounds weird)

        # End Placeholder

        # Check if player is on platform
        self.current_platform_hash = None
        current_platform_hash = self.find_current_platform()
        if not current_platform_hash:
            # Move to nearest platform and redo loop
            # Failed to find platform.
            self.platform_fail_loops += 1
            if self.platform_fail_loops >= self.platform_fail_loop_threshold:
                self.logger.debug("stuck. attempting unstick()...")
                self.unstick()
            return -1
        else:
            self.platform_fail_loops = 0
            self.current_platform_hash = current_platform_hash


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
        # Start inter-platform movement
        dest_platform_hash = random.choice([key for key in self.terrain_analyzer.platforms.keys() if key != current_platform_hash])
        dest_platform = self.terrain_analyzer.platforms[dest_platform_hash]
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

        # Other buffs
        self.player_manager.holy_symbol()
        self.player_manager.hyper_body()
        self.player_manager.release_overload()
        time.sleep(0.05)

        # Finished
        self.loop_count += 1
        return 0


