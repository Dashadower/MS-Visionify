

class PathAnalyzer:
    def __init__(self):
        self.platforms = []
        self.ladders = []
        self.visited_coordinates = []
        self.current_platform_coords = []
        self.current_ladder_coords = []
        self.last_x = None
        self.last_y = None
        self.movement = None
        self.determination_accuracy = 0
        self.platform_variance = 3
        self.ladder_variance = 2
        self.minimum_platform_length = 10
        self.minimum_ladder_length = 5
    def input(self, inp_x, inp_y):
        converted_tuple = (inp_x, inp_y)
        if converted_tuple not in self.visited_coordinates:
            self.visited_coordinates.append(converted_tuple)

        # check if in continous platform
        if inp_y == self.last_y and self.last_x >= self.last_x - self.platform_variance and self.last_x <= self.last_x + self.platform_variance:
            #check if current coordinate is within platform being tracked
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
    def reset(self):
        self.platforms = []
        self.visited_coordinates = []
        self.current_platform_coords = []
        self.current_ladder_coords = []
        self.ladders = []


