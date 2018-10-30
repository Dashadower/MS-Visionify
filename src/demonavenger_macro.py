# -*- coding:utf-8 -*-
from keystate_manager import KeyboardInputManager
from player_controller import PlayerController
from screen_processor import StaticImageProcessor, MapleScreenCapturer
from terrain_analyzer import PathAnalyzer
import os

class DemonAvengerMacro:
    """Master class for a Demon Avenger Macro. All macro related things are controlled from here"""
    def __init__(self):
        self.screen_capturer = MapleScreenCapturer()
        self.screen_processor = StaticImageProcessor(self.screen_capturer)
        self.keybd_mgr = KeyboardInputManager()
        self.player_movement_controller = PlayerController(self.keybd_mgr, self.screen_processor)
        self.path_analyzer = PathAnalyzer()


    def load_mapdata(self, data_path):
            self.path_analyzer.load(data_path)

    def initialize_map(self, set_focus=False):
        self.screen_processor.update_image(set_focus=set_focus, update_rect=True)
        self.screen_processor.get_minimap_rect()