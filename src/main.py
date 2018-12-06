import keystate_manager as km
import player_controller as pc
import screen_processor as sp
import terrain_analyzer as ta
import queue
class MacroController:
    def __init__(self, keymap=km.DEFAULT_KEY_MAP):
        self.screen_capturer = sp.MapleScreenCapturer()
        self.screen_processor = sp.StaticImageProcessor(self.screen_capturer)
        self.terrain_analyzer = ta.PathAnalyzer()
        self.keyhandler = km.KeyboardInputManager()
        self.player_manager = pc.PlayerController(self.keyhandler, self.screen_processor, keymap)


    def loop(self):
        """
        Main event loop for Macro
        :return: loop exit code
        """
        # Check if MapleStory window is alive
        if not self.screen_capturer.ms_get_screen_hwnd():
            self.abort()
            return 0

        # Update Screen
        self.screen_processor.update_image()

        # Update Constants
        player_minimap_pos = self.screen_processor.find_player_minimap_marker()

        self.player_manager.update(player_minimap_pos[0], player_minimap_pos[1])

        # Placeholder for Lie Dectector Detector (sounds weird)

        # End Placeholder

        # Placeholder for Rune Detector

        # End Placeholder

        # Check if player is on platform
        current_platform_hash = None

        for key, platform in self.terrain_analyzer.oneway_platforms:
            if self.player_manager.y == platform.start_y and \
                self.player_manager.x >= platform.start_x and \
                self.player_manager.x <= platform.end_x:
                current_platform_hash = platform.hash
                break

        for key, platform in self.terrain_analyzer.platforms:
            if self.player_manager.y == platform.start_y and \
                self.player_manager.x >= platform.start_x and \
                self.player_manager.x <= platform.end_x:
                current_platform_hash = platform.hash
                break

        if not current_platform_hash:
            # Move to nearest platform and redo loop
            return -1

        else:
            # Move to new platform
            goal = self.terrain_analyzer.select_move(current_platform_hash)
            if goal["method"] == "jumpr":
                move_distance = goal["lower_bound"][0] - self.player_manager.x
                if move_distance >= 20:


    def abort(self):
        pass
