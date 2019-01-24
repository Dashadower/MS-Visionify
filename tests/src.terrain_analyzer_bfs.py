import sys, os, time
sys.path.append("../src")
sys.path.append("C:\\Users\\tttll\\PycharmProjects\\MacroSTory")
from terrain_analyzer import PathAnalyzer
pathextractor = PathAnalyzer()
pathextractor.load("C:\\Users\\tttll\PycharmProjects\\MacroSTory\\tests\\본색을 드러내는 곳 2.platform")
print(__file__)
print(pathextractor.platforms)
pathextractor.calculate_navigation_map()
for key, val in pathextractor.platforms.items():
    print(key)
    print(val.solutions)
    print(val.last_visit)
    print("-------------------")

start_hash = input("current location?")
goal_hash = input("goal hash?")

for solution in pathextractor.pathfind(start_hash, goal_hash):
    print(solution.method, solution.to_hash)
