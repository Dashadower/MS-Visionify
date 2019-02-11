# -*- coding:utf-8 -*-
import terrain_analyzer, time

class Node:
    def __init__(self, x=None, y=None, g=None, h=None, path=[]):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = 0
        self.path = path
        if self.g:
            self.f = self.g + self.h
    def calculate_f(self):
        return self.g+self.h if self.g and self.h else 0

class PathPlanner:
    def __init__(self):
        self.map_grid = []
        self.map_width = 0
        self.map_height = 0

        self.doublejump_max_cost = 5
        self.doublejump_half_cost = 3
        self.drop_cost = 2
        self.horizontal_jump_cost = 1

        self.max_doublejump_height = 30

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
            map_grid.append([0 for x in range(width)])

        for key, platform in platforms.items():
            # currently this only uses the platform's start x and y coords and traces them until end x coords.
            for platform_coord in range(platform.start_x, platform.end_x + 1):
                map_grid[platform.start_y][platform_coord] = 1

        self.map_grid = map_grid

        return map_grid

    def astar(self, current_coordinate, goal_coordinate, map_grid=None):
        """
        Generates a solution from current_coordinate to goal_coordinate usign A* pathfinding
        :param current_coordinate: tuple of starting coordinate
        :param goal_coordinate: tuple of end coordinate
        :param map_grid: map list to use. If not supplied, will use pregenerated map grid from self.generate_map_grid
        :return: Solution list
        """
        if not map_grid and not self.map_grid:
            return 0
        elif map_grid:
            self.map_grid = map_grid

        open_list = set()
        closed_list = set()

        open_list.add(Node(current_coordinate[0], current_coordinate[1], g=0, h=0))

        while open_list:
            selection = min(open_list, key=lambda x: x.calculate_f())
            open_list.remove(selection)
            for coordinate, method in self.astar_find_proximity_pixels(selection.x, selection.y, goal_coordinate):
                successor_g = selection.g + self.astar_g(selection.x, selection.y, coordinate[0], coordinate[1])
                successor_h = self.astar_h(coordinate[0], coordinate[1], goal_coordinate[0], goal_coordinate[1])
                successor_path = selection.path + [(coordinate,method)]
                if coordinate == goal_coordinate:
                    return successor_path

                skip = False
                for existing_open_node in open_list:
                    if existing_open_node.x == coordinate[0] and existing_open_node.y == coordinate[1]:
                        if existing_open_node.f < successor_g + successor_h:
                            skip = True
                            break

                if skip:
                    continue
                for existing_closed_node in closed_list:
                    if existing_closed_node[0] == coordinate:
                        if existing_closed_node[1] < successor_g + successor_h:
                            skip = True
                            break
                if skip:
                    continue

                successor_node = Node(coordinate[0], coordinate[1], g=selection.g + successor_g, h=successor_h,path=successor_path)
                open_list.add(successor_node)

            closed_list.add(((selection.x, selection.y), selection.f))


    def astar_g(self, x1, y1, x2, y2):
        if y1 == y2:
            return abs(x1-x2)
        else:
            if y1 < y2:
                return abs(y1-y2) * 1.5
            elif y1 > y2:
                return abs(y1-y2)
    def astar_h(self, x1, y1, x2, y2):
        return (x1-x2)**2 + (y1-y2)**2

    def doublejump_cost(self, y1, y2):
        """
        Calcuates the time required to jump height |y1-y2|
        :param y1: y coordinate 1
        :param y2: y coordinate 2
        :return: time required to doublejump height |y1-y2|
        """
        absdiff = abs(y1-y2)

        linexp = -76.42857*absdiff + 41.92857
        # generated using linear regression

    def astar_find_proximity_pixels(self, x, y, goal_coordinate):
        """
        Finds all the pixels which can be reached from (x,y). Methods include horizontal movement, jump and dropping
        :param x: x coord
        :param y: y coord
        :param goal_coordinate: goal coordinate tuple
        :return: list of tuples (coord, method) where coord is a coordinate tuple, method
        """
        return_list = []
        # check horizontally touching pixels.
        x_increment = 1
        contiunue_check = True
        while contiunue_check:
            if x-x_increment == 0:
                return_list.append(((x-x_increment, y), "l"))
                break
            if (x-x_increment, y) == goal_coordinate:
                return_list.append(((x - x_increment, y), "l"))
                break
            if self.map_grid[y][x-x_increment] == 1:
                drop_distance = 1
                while True:
                    if y + drop_distance == len(self.map_grid) - 1:
                        break
                    if self.map_grid[y + drop_distance][x] == 1:
                        return_list.append(((x - x_increment, y), "l"))
                        contiunue_check = False
                        break
                    drop_distance += 1

                for jmpheight in range(1, self.max_doublejump_height):
                    if y - jmpheight == 0:
                        break

                    if self.map_grid[y - jmpheight][x-x_increment] == 1:
                        return_list.append(((x - x_increment, y), "l"))
                        contiunue_check = False
                        break
            else:
                return_list.append(((x - x_increment, y), "l"))
                break
            x_increment += 1

        x_increment = 0
        contiunue_check = True
        while contiunue_check:
            if x + x_increment == 0:
                new_coord = self.map_grid[y][x - x_increment]
                return_list.append(((x + x_increment, y), "r"))
                break
            if (x+x_increment, y) == goal_coordinate:
                return_list.append(((x + x_increment, y), "r"))
                break
            if self.map_grid[y][x + x_increment] == 1:
                drop_distance = 1
                while True:
                    if y + drop_distance == len(self.map_grid) - 1:
                        break
                    if self.map_grid[y + drop_distance][x] == 1:
                        return_list.append(((x + x_increment, y), "r"))
                        contiunue_check = False
                        break
                    drop_distance += 1

                for jmpheight in range(1, self.max_doublejump_height):
                    if y - jmpheight == 0:
                        break

                    if self.map_grid[y - jmpheight][x + x_increment] == 1:
                        return_list.append(((x + x_increment, y), "r"))
                        contiunue_check = False
                        break
            else:
                return_list.append(((x + x_increment, y), "r"))
                break
            x_increment += 1

        for jmpheight in range(1,self.max_doublejump_height):
            if y - jmpheight == 0:
                break

            if self.map_grid[y-jmpheight][x] == 1:
                return_list.append(((x, y-jmpheight), "dbljmp"))

        drop_distance = 1
        while True:
            if y + drop_distance == len(self.map_grid)-1:
                break
            if self.map_grid[y+drop_distance][x] == 1:
                return_list.append(((x, y + drop_distance), "drop"))
                break

            drop_distance += 1

        return return_list


if __name__ == "__main__":
    planner = PathPlanner()
    ct = planner.generate_map_grid(None, None, 100, 40)
    for row in ct:
        print(row)

