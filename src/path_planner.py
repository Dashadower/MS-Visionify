# -*- coding:utf-8 -*-
import terrain_analyzer, time, math

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
        self.astar_open_vals = []
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

        self.astar_open_vals = []
        for y in range(height):
            self.astar_open_vals.append([0 for x in range(width)])

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

        self.astar_open_vals = []
        for y in range(len(self.map_grid)):
            self.astar_open_vals.append([0 for x in range(len(self.map_grid[0])+1)])

        open_list = set()
        closed_set = set()
        open_set = set()
        open_list.add(Node(current_coordinate[0], current_coordinate[1], g=0, h=0))
        open_set.add(current_coordinate)

        while open_list:
            selection = min(open_list, key=lambda x: x.calculate_f())

            if selection.x == goal_coordinate[0] and selection.y == goal_coordinate[1]:
                return selection.path

            open_list.remove(selection)
            open_set.remove((selection.x, selection.y))
            closed_set.add((selection.x, selection.y))
            for coordinate, method in self.astar_find_proximity_pixels(selection.x, selection.y, goal_coordinate):
                if coordinate in closed_set:
                    continue
                successor_g = selection.g + self.astar_g(selection.x, selection.y, coordinate[0], coordinate[1])
                successor_h = self.astar_h(coordinate[0], coordinate[1], goal_coordinate[0], goal_coordinate[1])
                successor_path = selection.path + [(coordinate, method)]
                if coordinate in open_set:
                    if self.astar_open_vals[coordinate[1]][coordinate[0]] < successor_g:
                        continue

                successor_node = Node(coordinate[0], coordinate[1], g=selection.g + successor_g, h=successor_h,path=successor_path)
                open_list.add(successor_node)
                open_set.add(coordinate)
                if self.astar_open_vals[coordinate[1]][coordinate[0]] > successor_g:
                    self.astar_open_vals[coordinate[1]][coordinate[0]] = successor_g



    def astar_g(self, x1, y1, x2, y2):
        if y1 == y2:
            return abs(x1-x2)
        else:
            if y1 < y2:
                return abs(y1-y2)# * 1.5
            elif y1 > y2:
                return abs(y1-y2)# * 1.2

    def astar_h(self, x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
        #return abs(x1-x2) + abs(y1-y2)

    def doublejump_cost(self, y1, y2):
        """
        Calcuates the time required to jump height |y1-y2|
        :param y1: y coordinate 1
        :param y2: y coordinate 2
        :return: time required to doublejump height |y1-y2|
        """
        absdiff = abs(y1-y2)

        # Some info on equation
        # regression for y bar where y is jump height and t is delay in seconds
        # y = -76.42857t + 41.92857
        # solved for t and simplified
        # t = -(y - 41.9)/76.4

        t = round(-(absdiff - 41.9)/76.4, 2)
        if t >= 0.45:
            t = 0.45
        return t

    def jump_double_curve(self, start_x, start_y, current_x):
        """
        Calculates the height at horizontal double jump starting from(start_x, start_y) at x coord current_x
        :param start_x: start x coord
        :param start_y: start y coord
        :param current_x: x of coordinate to calculate height
        :return: height at current_x
        """
        slope = 0.05
        x_jump_range = 10 if current_x > start_x else -10
        y_jump_height = 1.4
        max_coord_x = (start_x*2 + x_jump_range)/2
        max_coord_y = start_y - y_jump_height
        if max_coord_y <= 0:
            return 0

        y = slope * (current_x - max_coord_x)**2 + max_coord_y
        return max(0, y)

    def distance(self, coord1, coord2):
        return math.sqrt((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)

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
                return_list.append(((x-x_increment + 1, y), "l"))
                break
            if (x-x_increment, y) == goal_coordinate:
                return_list.append(((x - x_increment, y), "l"))
                break

            if self.map_grid[y][x-x_increment] == 1:
                drop_distance = 1
                while True:
                    if y + drop_distance >= len(self.map_grid) - 1:
                        break
                    if self.map_grid[y + drop_distance][x] == 1:
                        return_list.append(((x - x_increment, y), "l"))
                        contiunue_check = False
                        break
                    drop_distance += 1

                for jmpheight in range(1, self.max_doublejump_height+1):
                    if y - jmpheight <= 0:
                        break

                    if self.map_grid[y - jmpheight][x-x_increment] == 1:
                        return_list.append(((x - x_increment, y), "l"))
                        contiunue_check = False
                        break
            else:
                if x_increment != 1:
                    return_list.append(((x - x_increment, y), "l"))
                break
            x_increment += 1

        x_increment = 1
        contiunue_check = True
        while contiunue_check:
            if x + x_increment == 0:
                return_list.append(((x + x_increment - 1, y), "r"))
                break
            if (x+x_increment, y) == goal_coordinate:
                return_list.append(((x + x_increment, y), "r"))
                break
            if self.map_grid[y][x + x_increment] == 1:
                drop_distance = 1
                while True:
                    if y + drop_distance >= len(self.map_grid) - 1:
                        break
                    if self.map_grid[y + drop_distance][x] == 1:
                        return_list.append(((x + x_increment, y), "r"))
                        contiunue_check = False
                        break
                    drop_distance += 1

                for jmpheight in range(1, self.max_doublejump_height+1):
                    if y - jmpheight <= 0:
                        break

                    if self.map_grid[y - jmpheight][x + x_increment] == 1:
                        return_list.append(((x + x_increment, y), "r"))
                        contiunue_check = False
                        break
            else:
                if x_increment != 1:
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

        # check if doublejump leads us to another platform
        jump_height = 6
        for x_increment in [1, -1]:
            while True:
                if x + x_increment >= self.map_width-1 or x+x_increment == 0:
                    break
                jump_y = max(0, int(self.jump_double_curve(x, y-jump_height, x+x_increment)))
                if jump_y >= self.map_height-1:
                    break
                if self.map_grid[jump_y][x+x_increment] == 1:
                    return_list.append(((x+x_increment, jump_y), "horjmp"))
                    break
                if x_increment < 0:
                    x_increment -= 1
                else:
                    x_increment += 1
        return return_list


if __name__ == "__main__":
    planner = PathPlanner()
    ct = planner.generate_map_grid(None, None, 100, 40)
    for row in ct:
        print(row)

