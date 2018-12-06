import sys
sys.path.append("../src")
sys.path.append("C:\\Users\\Administrator\\PycharmProjects\\MacroStory")
from src.terrain_analyzer import PathAnalyzer
import time, os
pathextractor = PathAnalyzer()
pathextractor.load("C:\\Users\Administrator\\PycharmProjects\\MacroStory\\tests\\mapdata.platform")

print(pathextractor.platforms)
pathextractor.calculate_navigation_map()
for key, val in pathextractor.platforms.items():
    print(key)
    print(val.solutions)
    print(val.last_visit)
    print("-------------------")

start_hash = input("current location?")

while True:
    os.system("cls")
    print("result of select_move of start hash:")
    optimal = pathextractor.select_move(start_hash)
    print(optimal)
    print("current location:", start_hash)
    print("moving to       :", optimal["hash"])
    pathextractor.move_platform(start_hash, optimal["hash"])
    start_hash = optimal["hash"]
    print("--------------")
    for key, val in pathextractor.platforms.items():
        print(key)
        for obj in val.solutions:
            print(obj)
        print("last visit:", val.last_visit if val.last_visit <= len(pathextractor.platforms) * 2 -1 else "@@@@@@" + str(val.last_visit))
        print("-------------------")

    time.sleep(1)
