import sys, os, time
sys.path.append("../src")
sys.path.append("C:\\Users\\tttll\\PycharmProjects\\MacroSTory")
from terrain_analyzer import PathAnalyzer
pathextractor = PathAnalyzer()
pathextractor.load("풍화된_기쁨과_분노의_땅.platform")
print(__file__)
print(pathextractor.platforms)
pathextractor.calculate_navigation_map()
for key, val in pathextractor.platforms.items():
    print(key, val.start_x, val.start_y, val.end_x,val.end_y)
    print(val.solutions)
    print(val.last_visit)
    print("-------------------")

start_hash = input("current location?")
goal_hash = input("goal hash?")

for solution in pathextractor.pathfind(start_hash, goal_hash):
    print(solution.method, solution.to_hash)
