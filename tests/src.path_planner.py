import sys, os, time
import tkinter as tk
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

maplist = planner.generate_map_grid(pathextractor.platforms, None, minimap_roi[2], minimap_roi[3])

root = tk.Tk()
cv = tk.Canvas(root)
cv.pack(expand="yes", fill="both")

tile_size = root.winfo_screenwidth()/minimap_roi[2]
def render():
    cv.delete("all")
    for row in range(len(maplist)):
        for column in range(len(maplist[0])):
            if maplist[row][column] == 1:
                cv.create_rectangle(column*tile_size, row*tile_size, (column+1)*tile_size, (row+1)*tile_size, fill="red")
            else:
                cv.create_rectangle(column*tile_size, row*tile_size, (column+1)*tile_size, (row+1)*tile_size, fill="white")

clickmode = 1
start_coord = (142,27)
end_coord = (80,8)
def onclick(event):
    global clickmode, start_coord, end_coord
    if clickmode == 1:
        start_coord = (int(event.x/tile_size), int(event.y/tile_size))
        cv.create_rectangle(start_coord[0] * tile_size, start_coord[1] * tile_size, (start_coord[0] + 1) * tile_size,
                            (start_coord[1] + 1) * tile_size, fill="green")
        clickmode = -1
    else:
        print("reached")
        end_coord = (int(event.x/tile_size), int(event.y/tile_size))
        clickmode = 1
        render()
        print("pathfinding", start_coord, end_coord)
        s = time.time()
        path = planner.astar(start_coord, end_coord)
        e = time.time()
        print("time", e-s)
        for method in path:
            start_coord = method[0]
            cv.create_rectangle(start_coord[0] * tile_size, start_coord[1] * tile_size,
                                (start_coord[0] + 1) * tile_size,
                                (start_coord[1] + 1) * tile_size, fill="green")

render()
cv.bind("<Button-1>", onclick)
"""start_coord = (64, 38)
end_coord = (168, 27)
print(planner.astar_find_proximity_pixels(start_coord[0], start_coord[1]))
tile_size = 8
path = planner.astar(start_coord, end_coord)

for method in path:
    start_coord = method[0]
    print(method)"""


root.mainloop()



