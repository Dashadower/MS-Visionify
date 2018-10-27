import math, pickle, os

class PathAnalyzer:
    def __init__(self):
        self.platforms = []
        self.oneway_platforms = []
        self.ladders = []
        self.visited_coordinates = []
        self.current_platform_coords = []
        self.current_oneway_coords = []
        self.current_ladder_coords = []
        self.last_x = None
        self.last_y = None
        self.movement = None

        self.determination_accuracy = 0
        self.platform_variance = 3
        self.ladder_variance = 2
        self.minimum_platform_length = 10
        self.minimum_ladder_length = 5

        self.doublejump_height = 31  # total absolute jump height is about 31, but take account platform size
        self.jump_range = 16  # horizontal jump distance is about 9~10 EDIT:now using glide jump which has more range
        self.dbljump_range = 15 # not in use

    def save(self, filename="mapdata.platform", minimap_roi = None):
        with open(filename, "wb") as f:
            pickle.dump({"platforms" : self.platforms, "oneway": self.oneway_platforms, "minimap" : minimap_roi}, f)

    def load(self, filename="mapdata.platform"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                data = pickle.load(f)
                self.platforms = data["platforms"]
                self.oneway_platforms = data["oneway"]
                minimap_coords = data["minimap"]
            return minimap_coords 

    def input_oneway_platform(self, inp_x, inp_y):
        """input values to use in finding one way(platforms which can't be a destination platform)"""
        converted_tuple = (inp_x, inp_y)
        if converted_tuple not in self.visited_coordinates:
            self.visited_coordinates.append(converted_tuple)

        # check if in continous platform
        if inp_y == self.last_y and self.last_x >= self.last_x - self.platform_variance and self.last_x <= self.last_x + self.platform_variance:
            # check if current coordinate is within platform being tracked
            if converted_tuple not in self.current_oneway_coords:
                self.current_oneway_coords.append(converted_tuple)
        else:
            # current coordinates do not belong in any platforms
            # terminate pending platform, if exists and create new pending platform
            if len(self.current_oneway_coords) >= self.minimum_platform_length:
                platform_start = min(self.current_oneway_coords, key=lambda x: x[0])
                platform_end = max(self.current_oneway_coords, key=lambda x: x[0])

                self.oneway_platforms.append((platform_start, platform_end))
            self.current_oneway_coords = []
            if converted_tuple not in self.visited_coordinates:
                self.current_oneway_coords.append(converted_tuple)


    def input(self, inp_x, inp_y):
        converted_tuple = (inp_x, inp_y)
        if converted_tuple not in self.visited_coordinates:
            self.visited_coordinates.append(converted_tuple)

        # check if in continous platform
        if inp_y == self.last_y and self.last_x >= self.last_x - self.platform_variance and self.last_x <= self.last_x + self.platform_variance:
            # check if current coordinate is within platform being tracked
            if converted_tuple not in self.current_platform_coords:
                self.current_platform_coords.append(converted_tuple)
        else:
            # current coordinates do not belong in any platforms
            # terminate pending platform, if exists and create new pending platform
            if len(self.current_platform_coords) >= self.minimum_platform_length:
                platform_start = min(self.current_platform_coords, key=lambda x: x[0])
                platform_end = max(self.current_platform_coords, key=lambda x: x[0])

                self.platforms.append((platform_start, platform_end))
            self.current_platform_coords = []
            if converted_tuple not in self.visited_coordinates:
                self.current_platform_coords.append(converted_tuple)

        # check if in continous ladder
        if inp_x == self.last_x and inp_y >= self.last_y - self.ladder_variance and inp_y <= self.last_y + self.ladder_variance:
            # current coordinate is within pending group of coordinates for a ladder or a rope or whatever
            if converted_tuple not in self.current_ladder_coords:
                self.current_ladder_coords.append(converted_tuple)
        else:
            # current coordinates do not belong in any ladders or ropes
            # terminate ladder or ropes
            if len(self.current_ladder_coords) >= self.minimum_ladder_length:
                ladder_start = min(self.current_ladder_coords, key=lambda x: x[1])
                ladder_end = max(self.current_ladder_coords, key=lambda x: x[1])
                self.ladders.append((ladder_start, ladder_end))
            self.current_ladder_coords = []
            if converted_tuple not in self.visited_coordinates:
                self.current_ladder_coords.append(converted_tuple)
        self.last_x = inp_x
        self.last_y = inp_y

    def find_available_moves(self, platform):
        """Find relationships between platform, like how one platform links to another using movement.
        : param platform : platform item in self.platforms (tuple of 2 coordinate tuples)
        : return : list [destination_platform, (x1, y1), (x2, y2), method] where
        destination_platform : platform object in self.platforms which is the destination
        x, y : coordinate area where the method can be used (x1<=coord_x<=x2, y1<=coord_y<=y2)
        method : movement method string
            drop : drop down directly
            jmpr : right jump
            jmpl : left jump
            dbljmp : double jump up
        """

        return_map_dict = []

        for other_platform in self.platforms:
            if platform != other_platform:
                # 1. Detect vertical overlaps
                if platform[0][0] < other_platform[1][0] and platform[1][0] > other_platform[0][0] or \
                        platform[0][0] > other_platform[0][0] and platform[0][0] < other_platform[1][0]:
                    lower_bound_x = max(platform[0][0], other_platform[0][0])
                    upper_bound_x = min(platform[1][0], other_platform[1][0])
                    if platform[0][1] < other_platform[1][1]:
                        # Platform is higher than current_platform. Thus we can just drop
                        solution = [other_platform, (lower_bound_x, platform[0][1]), (upper_bound_x, platform[0][1]), "drop"]
                        return_map_dict.append(solution)
                    else:
                        # We need to use double jump to get there, but first check if within jump height
                        if abs(platform[0][1] - other_platform[0][1]) <= self.doublejump_height:
                            solution = [other_platform, (lower_bound_x, platform[0][1]), (upper_bound_x, platform[0][1]), "dbljmp"]
                            return_map_dict.append(solution)
                else:
                    # 2. No vertical overlaps. Calculate euclidean distance between each platform endpoints
                    front_point_distance = math.sqrt((platform[0][0]-other_platform[1][0])**2 + (platform[0][1]-other_platform[1][1])**2)
                    if front_point_distance <= self.jump_range:
                        # We can jump from the left end of the platform to goal
                        solution = [other_platform, (platform[0][0], platform[0][1]), (platform[0][0], platform[0][1]), "jmpl"]
                        return_map_dict.append(solution)
                    back_point_distance = math.sqrt((platform[1][0]-other_platform[0][0])**2 + (platform[1][1]-other_platform[0][1])**2)
                    if back_point_distance <= self.jump_range:
                        # We can jump fomr the right end of the platform to goal platform
                        solution = [other_platform, (platform[1][0], platform[1][1]), (platform[1][0], platform[1][1]), "jmpr"]
                        return_map_dict.append(solution)

        return return_map_dict

    def reset(self):
        self.platforms = []
        self.visited_coordinates = []
        self.current_platform_coords = []
        self.current_ladder_coords = []
        self.ladders = []

