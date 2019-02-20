import sys, os, time
sys.path.append("../src")
sys.path.append("C:\\Users\\tttll\\PycharmProjects\\MacroSTory")
from terrain_analyzer import PathAnalyzer
pathextractor = PathAnalyzer()
pathextractor.load("본색을 드러내는 곳 2.platform")
print(__file__)
print(pathextractor.platforms)
pathextractor.generate_solution_dict()
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

    time.sleep(5)
