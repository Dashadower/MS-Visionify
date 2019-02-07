import sys, os, time
sys.path.append("../src")
sys.path.append("C:\\Users\\tttll\\PycharmProjects\\MacroSTory")
from terrain_analyzer import PathAnalyzer
from path_planner import PathPlanner
pathextractor = PathAnalyzer()
planner = PathPlanner()
minimap_roi = pathextractor.load("풍화된_기쁨과_분노의_땅.platform")
print(__file__)
print(pathextractor.platforms)
pathextractor.generate_solution_dict()
for key, val in pathextractor.platforms.items():
    print(key, val.start_x, val.start_y, val.end_x, val.end_y)
    print("-------------------")

for row in planner.generate_map_grid(pathextractor.platforms, None, minimap_roi[2], minimap_roi[3]):
    print(row)

