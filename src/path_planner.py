# -*- coding:utf-8 -*-
import terrain_analyzer

class PathPlanner:
    def __init__(self):
        self.map_grid = []
        self.map_width = 0
        self.map_height = 0

        self.doublejump_max_cost = 5
        self.doublejump_half_cost = 3
        self.drop_cost = 2
        self.horizontal_jump_cost = 1

    def generate_map_grid(self, platforms, oneway_platforms, width, height):
        """
        Generates a map grid from input parameters
        :param platforms: list of terrain_analyzer Platform object
        :param oneway_platforms: list of terrain_analyzer Platform object, oneway
        :param width: width of map
        :param height: height of map
        :return: map_grid: list of lists representing map where each element is 1 if platform, 0 if empty.
        """
        self.map_width = width
        self.map_height = height

        map_grid = []
        for y in range(height):
            map_grid.append([])
            for x in range(width):
                map_grid[y].append(0)

        for key, platform in platforms.items():
            # currently this only uses the platform's start x and y coords and traces them until end x coords.
            for platform_coord in range(platform.start_x, platform.end_x + 1):
                map_grid[platform.start_y][platform_coord] = 1

        return map_grid


if __name__ == "__main__":
    planner = PathPlanner()
    ct = planner.generate_map_grid(None, None, 100, 40)
    for row in ct:
        print(row)

