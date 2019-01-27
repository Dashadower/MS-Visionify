import math, pickle, os, hashlib, random

"""
PlatformScan, graph based least-visited-node-first traversal algorithm
Let map(V,E) be a directed cyclic graph
function traverse(from, to):
    from[to].visited = 1
    map[to].last_visit = 0
    for node in map:
        node.last_visit += 1
    need_reset = True
    for vert in from.vertices:
        if vert.visited == 0:
            need_reset = False
            break
    
    if need_reset:
        for vert in from.vertices:
            vert.visited = 0

function select(current_node):
    for vert in sorted(current_node.vertices, key=lambda x:vert.last_visit):
        if vert.visited = 0:
            return vert
"""

METHOD_DROP = "drop"
METHOD_DBLJMP_MAX = "dbljmp_max"
METHOD_DBLJMP_HALF = "dbljmp_half"
METHOD_JUMPR = "jumpr"
METHOD_JUMPL = "jumpl"

class Platform:
    def __init__(self, start_x = None, start_y = None, end_x = None, end_y = None, last_visit = None, solutions = None, hash = None):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.last_visit = last_visit # list of a list: [solution, 0]
        self.solutions = solutions
        self.hash = hash

class Solution:
    def __init__(self, from_hash=None, to_hash=None, lower_bound=None, upper_bound=None, method=None, visited=False):
        self.from_hash = from_hash
        self.to_hash = to_hash
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.method = method
        self.visited = visited

class PathAnalyzer:
    """Converts minimap player coordinates to terrain information like ladders and platforms."""
    def __init__(self):
        """
        Difference between self.platforms and self.oneway_platforms: platforms can be a destination and an origin.
        However, oneway_platforms can only be an origin. oneway_platforms can be used to detect when player goes out of bounds.
        self.platforms: list of tuples, where tuple[0] is starting coordinate of platform, tuple[1] is end coordinate.

        """
        self.platforms = {} # Format: hash, Platform()
        self.oneway_platforms = {}
        self.ladders = []
        self.visited_coordinates = []
        self.current_platform_coords = []
        self.current_oneway_coords = []
        self.current_ladder_coords = []
        self.last_x = None
        self.last_y = None
        self.movement = None

        self.determination_accuracy = 0  # Offset to determine y coord accuracy NOT USED
        self.platform_variance = 3
        self.ladder_variance = 2
        self.minimum_platform_length = 10  # Minimum x length of coordinates to be logged as a platform by input()
        self.minimum_ladder_length = 5  # Minimum y length of coordinated to be logged as a ladder by input()

        self.dbljump_max_height = 31  # total absolute jump height is about 31, but take account platform size
        self.jump_range = 16  # horizontal jump distance is about 9~10 EDIT:now using glide jump which has more range
        self.dbljump_half_height = 20  # absolute jump height of a half jump. Used for generating navigation map

    def save(self, filename="mapdata.platform", minimap_roi = None):
        """Save platforms, oneway_platforms, ladders, minimap_roi to a file
        :param filename: path to save file
        :param minimap_roi: tuple or list of onscreen minimap bounding box coordinates which will be saved"""
        with open(filename, "wb") as f:
            pickle.dump({"platforms" : self.platforms, "oneway": self.oneway_platforms, "minimap" : minimap_roi}, f)

    def load(self, filename="mapdata.platform"):
        """Open a map data file and load data from file
        :param filename: Plath to map data file
        :return boundingRect tuple of minimap as stored on file"""
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                data = pickle.load(f)
                self.platforms = data["platforms"]
                self.oneway_platforms = data["oneway"]
                minimap_coords = data["minimap"]
            return minimap_coords 

    def verify_data_file(self, filename):
        """
        Verify a platform file to see if it is in correct format
        :param filename: file path
        :return: 0 if valid, 1 if corrupt or errored
        """
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                try:
                    data = pickle.load(f)
                    platforms = data["platforms"]
                    oneway_platforms = data["oneway"]
                    minimap_coords = data["minimap"]
                except:
                    return 1
            return minimap_coords
        else:
            return 1


    def hash(self, data):
        """
        Returns salted md5 hash of data
        :param data: String to be hashed
        :return: hexdigest string MD5 hash
        """
        d_hash = hashlib.md5()
        d_hash.update((str(data) + str(random.random())).encode())
        return str(d_hash.hexdigest())[:8]

    def pathfind(self, start_hash, goal_hash):
        """
        Simple BFS algorithm to find a path from start platform to goal platform.
        :param start_hash: hash of starting platform
        :param goal_hash:  hash of goal platform
        :return: list, in order of solutions to reach goal
        """

        try:
            start_platform = self.platforms[start_hash]
        except KeyError:
            start_platform = self.oneway_platforms[start_hash]
        max_steps = len(self.platforms) + len(self.oneway_platforms) + 2
        calculated_paths = []
        bfs_queue = []
        visited_platform_hashes = []
        for solution in start_platform.solutions:
            if solution.to_hash not in visited_platform_hashes:
                bfs_queue.append([solution, [solution]])

        while bfs_queue:
            current_solution, paths = bfs_queue.pop()
            visited_platform_hashes.append(current_solution.from_hash)
            if current_solution.to_hash == goal_hash:
                calculated_paths.append(paths)
            try:
                next_solution = self.platforms[current_solution.to_hash].solutions
            except KeyError:
                next_solution = self.oneway_platforms[current_solution.to_hash].solutions
            for solution in next_solution:
                if solution.to_hash not in visited_platform_hashes:
                    cv = paths
                    cv.append(solution)
                    bfs_queue.append([solution, cv])

        if calculated_paths:
            return sorted(calculated_paths, key=lambda x: len(x))[0]
        else:
            return calculated_paths


    def calculate_navigation_map(self):
        """Generates a navigation map, which is a dictionary with platform as keys and a dictionary of a list[strategy, 0]"""
        for key, platform in self.platforms.items():
            platform.last_visit = 0
            self.calculate_interplatform_solutions(key)
        for key, platform in self.oneway_platforms.items():
            self.calculate_interplatform_solutions(key, oneway=True)

    def move_platform(self, from_platform, to_platform):
        """Update navigation map visit counter to keep track of visited platforms when moded
        :param from_platform: departing platform hash
        :param to_platform: destination platform hash"""

        need_reset = True
        try:
            for method in self.platforms[from_platform].solutions:
                solution = method
                if solution.to_hash == to_platform:
                    self.platforms[solution.to_hash].last_visit = 0
                    method.visited = True

                else:
                    if not method.visited:
                        need_reset = False
        except:
            need_reset = False
            pass

        for key, platform in self.platforms.items():
            if key != to_platform and key != from_platform:
                self.platforms[key].last_visit += 1
        if need_reset:
            for method in self.platforms[from_platform].solutions:
                method.visited = False



    def select_move(self, current_platform):
        """
        Selects a solution from current_platform using PlatformScan
        :param current_platform: hash of departing platform
        :return: solution list in solution array of current_playform
        """
        try:
            for solution in sorted(self.platforms[current_platform].solutions, key= lambda x: self.platforms[x.to_hash].last_visit, reverse=True):
                """if not solution.visited:
                    return solution"""
                return solution
        except KeyError:
            for solution in sorted(self.oneway_platforms[current_platform].solutions, key= lambda x: self.platforms[x.to_hash].last_visit, reverse=True):
                """if not solution.visited:
                    return solution"""
                return solution

    def input_oneway_platform(self, inp_x, inp_y):
        """input values to use in finding one way(platforms which can't be a destination platform)
        Refer to input() to see how it works
        :param inp_x: x coordinate to log
        :param inp_y: y coordinate to log"""
        converted_tuple = (inp_x, inp_y)
        if converted_tuple not in self.visited_coordinates:
            self.visited_coordinates.append(converted_tuple)

        # check if in continous platform
        if inp_y >= self.last_y-2 and inp_y <= self.last_y+2 and self.last_x >= self.last_x - self.platform_variance and self.last_x <= self.last_x + self.platform_variance:
            # check if current coordinate is within platform being tracked
            if converted_tuple not in self.current_oneway_coords:
                self.current_oneway_coords.append(converted_tuple)
        else:
            # current coordinates do not belong in any platforms
            # terminate pending platform, if exists and create new pending platform
            if len(self.current_oneway_coords) >= self.minimum_platform_length-1:
                platform_start = min(self.current_oneway_coords, key=lambda x: x[0])
                platform_end = max(self.current_oneway_coords, key=lambda x: x[0])
                d_hash = self.hash(str(platform_start))
                self.oneway_platforms[d_hash] = Platform(platform_start[0], platform_start[1], platform_end[0],
                                                  platform_end[1], 0, [], d_hash)
            self.current_oneway_coords = []
            if converted_tuple not in self.visited_coordinates:
                self.current_oneway_coords.append(converted_tuple)

    def input(self, inp_x, inp_y):
        """Use player minimap coordinates to determine start and end of platforms
        This function logs player minimap marker coordinates in an attempt to identify platform coordinates from them.
        Player coordinates are temoporarily logged to self.current_platform_coords until a platform is determined for
        the given set of coordinates.
        Given that all platforms are parallel to the ground, meaning all coordinates of the platform are on the same
        elevation, a collection of input player coordinates are deemed to be on a same platform until a change in y
        coordinates is detected.
        :param inp_x: x player minimap coordinate to log
        :param inp_y: y player minimap coordinate to log"""
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

                d_hash = self.hash(str(platform_start))
                self.platforms[d_hash] = Platform(platform_start[0], platform_start[1], platform_end[0], platform_end[1], 0, [], d_hash)

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

    def calculate_interplatform_solutions(self, hash, oneway=False):
        """Find relationships between platform, like how one platform links to another using movement.
        :param platform : platform hash in self.platforms Platform
        :return : None
        destination_platform : platform object in self.platforms which is the destination
        x, y : coordinate area where the method can be used (x1<=coord_x<=x2, y1<=coord_y<=y2)
        method : movement method string
            drop : drop down directly
            jmpr : right jump
            jmpl : left jump
            dbljmp_max : double jump up fully
            dbljmp_half : double jump a bit less
        """

        return_map_dict = []
        if oneway:
            platform = self.oneway_platforms[hash]
        else:
            platform = self.platforms[hash]
        platform.solutions = []
        for key, other_platform in self.platforms.items():
            if platform.hash != key:
                # 1. Detect vertical overlaps
                if platform.start_x < other_platform.end_x and platform.end_x > other_platform.start_x or \
                        platform.start_x > other_platform.start_x and platform.start_x < other_platform.end_x:
                    lower_bound_x = max(platform.start_x, other_platform.start_x)
                    upper_bound_x = min(platform.end_x, other_platform.end_x)
                    if platform.start_y < other_platform.end_y:
                        # Platform is higher than current_platform. Thus we can just drop
                        #solution = {"hash":key, "lower_bound":(lower_bound_x, platform.start_y), "upper_bound":(upper_bound_x, platform.start_y), "method":"drop", "visited" : False}
                        solution = Solution(platform.hash, key, (lower_bound_x, platform.start_y), (upper_bound_x, platform.start_y), METHOD_DROP, False)
                        # Changed to using classes for readability
                        platform.solutions.append(solution)
                    else:
                        # We need to use double jump to get there, but first check if within jump height
                        if abs(platform.start_y - other_platform.start_y) <= self.dbljump_half_height:
                            #solution = {"hash":key, "lower_bound":(lower_bound_x, platform.start_y), "upper_bound":(upper_bound_x, platform.start_y), "method":"dbljmp_half", "visited" : False}
                            solution = Solution(platform.hash, key, (lower_bound_x, platform.start_y), (upper_bound_x, platform.start_y), METHOD_DBLJMP_HALF, False)
                            platform.solutions.append(solution)
                        elif abs(platform.start_y - other_platform.start_y) <= self.dbljump_max_height:
                            #solution = {"hash": key, "lower_bound": (lower_bound_x, platform.start_y),"upper_bound": (upper_bound_x, platform.start_y), "method": "dbljmp_max", "visited" : False}
                            solution = Solution(platform.hash, key, (lower_bound_x, platform.start_y), (upper_bound_x, platform.start_y), METHOD_DBLJMP_MAX, False)
                            platform.solutions.append(solution)
                else:
                    # 2. No vertical overlaps. Calculate euclidean distance between each platform endpoints
                    front_point_distance = math.sqrt((platform.start_x-other_platform.end_x)**2 + (platform.start_y-other_platform.end_y)**2)
                    if front_point_distance <= self.jump_range:
                        # We can jump from the left end of the platform to goal
                        #solution = {"hash":key, "lower_bound":(platform.start_x, platform.start_y), "upper_bound":(platform.start_x, platform.start_y), "method":"jmpl", "visited" : False}
                        solution = Solution(platform.hash, key, (platform.start_x, platform.start_y), (platform.start_x, platform.start_y), METHOD_JUMPL, False)
                        platform.solutions.append(solution)

                    back_point_distance = math.sqrt((platform.end_x-other_platform.start_x)**2 + (platform.end_y-other_platform.start_y)**2)
                    if back_point_distance <= self.jump_range:
                        # We can jump fomr the right end of the platform to goal platform
                        solution = {"hash":key, "lower_bound":(platform.end_x, platform.end_y), "upper_bound":(platform.end_x, platform.end_y), "method":"jmpr", "visited" : False}
                        solution = Solution(platform.hash, key, (platform.end_x, platform.end_y), (platform.end_x, platform.end_y), METHOD_JUMPR, False)
                        platform.solutions.append(solution)



    def reset(self):
        """
        Reset all platform data to default
        :return: None
        """
        self.platforms = {}
        self.oneway_platforms = {}
        self.visited_coordinates = []
        self.current_platform_coords = []
        self.current_ladder_coords = []
        self.ladders = []

