# -*- coding:utf-8 -*-
from keystate_manager import KeyboardInputManager
from player_controller import PlayerController
from screen_processor import StaticImageProcessor, MapleScreenCapturer
from terrain_analyzer import PathAnalyzer
import directinput_constants, random, time

class DemonAvengerMacro:
    """Master class for a Demon Avenger Macro. All macro related things are controlled from here"""
    def __init__(self, loghandle=None):
        self.screen_capturer = MapleScreenCapturer()
        self.screen_processor = StaticImageProcessor(self.screen_capturer)
        self.keybd_mgr = KeyboardInputManager()
        self.player_movement_controller = PlayerController(self.keybd_mgr, self.get_player_minimap_coords)
        self.path_analyzer = PathAnalyzer()
        self.player_xpos = None
        self.player_ypos = None
        self.log_handle = loghandle
        self.current_platform = None
        self.origin_platform = None
        self.destination_platform = None

    def initialize_mapdata(self, map_data_path):
        self.path_analyzer.load(map_data_path)
        self.path_analyzer.calculate_navigation_map()

    def find_current_platform(self):
        for platform in self.path_analyzer.platforms + self.path_analyzer.oneway_platforms:
            if self.player_xpos >= platform[0][0] and self.player_xpos <= platform[1][0]:
                if self.player_ypos == platform[0][1]:
                    return platform

        return 0

    def get_advanced_strategies(self, from_platform):
        strategies = self.path_analyzer.navigation_map[from_platform]
        if len(strategies) == 1:
            return strategies

        unvisited_strategies = []
        for strategy in strategies:
            if not strategy[1]:
                unvisited_strategies.append(strategy[0])

        return unvisited_strategies

    def update(self):
        self.screen_processor.update_image(set_focus=False, update_rect=True)
        pcoords = self.screen_processor.find_player_minimap_marker(rect=self.screen_processor.minimap_rect)
        if pcoords:
            self.player_xpos = pcoords[0]
            self.player_ypos = pcoords[1]
            self.path_analyzer.input(pcoords[0], pcoords[1])

    def get_player_minimap_coords(self):
        self.update()
        return self.player_xpos, self.player_ypos

    def escape_stuck(self):
        method = random.randint(1, 5)
        if method == 1:
            self.keybd_mgr.single_press(directinput_constants.DIK_LEFT, 2)
        elif method == 2:
            self.keybd_mgr.single_press(directinput_constants.DIK_RIGHT, 2)
        elif method == 3:
            self.player_movement_controller.drop()
        elif method == 4:
            self.player_movement_controller.dbljump_max()

    def move_platform(self):
        self.origin_platform = self.current_platform
        strategies = self.get_advanced_strategies(self.current_platform)
        if len(strategies) > 1:
            choice = random.choice(strategies)[0]
            method = choice[3]
        else:
            choice = strategies[0][0]
            method = choice[3]

        self.update()
        xcoord = random.randint(choice[1][0], choice[2][0])
        self.player_movement_controller.horizontal_move_goal(xcoord)
        time.sleep(0.3)
        last_posx = self.player_xpos
        last_posy = self.player_ypos
        if method == "drop":
            self.player_movement_controller.drop()
        elif method == "dbljmp_max":
            self.player_movement_controller.dbljump_max()
        elif method == "dbljmp_half":
            self.player_movement_controller.dbljump_half()
        elif method == "jmpr":
            self.player_movement_controller.jumpr_double()
        elif method == "jmpl":
            self.player_movement_controller.jumpl_double()
        while True:
            self.update()
            new_xpos = self.player_xpos
            new_ypos = self.player_ypos
            if new_xpos == last_posx and new_ypos == last_posy:
                print("done")
                break
            last_posx = new_xpos
            last_posy = new_ypos

    def start(self):
        while True:
            self.update()
            current_platform = self.find_current_platform()

            if not current_platform:
                self.log_handle("Failed to find platform. Attempting random movement")
                self.escape_stuck()
                time.sleep(2)
            else:
                self.current_platform = current_platform
                break

        self.move_platform()


time.sleep(2)
print("start")
dt = DemonAvengerMacro()
dt.initialize_mapdata("../tests/mapdata.platform")
#print(dt.path_analyzer.platforms, dt.path_analyzer.oneway_platforms)
dt.start()


