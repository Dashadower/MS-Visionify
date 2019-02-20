from matplotlib import pyplot as plt
import numpy as np

jmp_coords = [(102, 49), (102, 48), (104, 47), (109, 47), (112, 48)]
x_val = [x[0] for x in jmp_coords]
y_val = [y[1] for y in jmp_coords]
#x = np.linspace(start_x, end_x, 500)
#y = (0.53*(x-((start_x+end_x)/2)))**2 + start_y - 7.3
plt.scatter(x_val, y_val)
#plt.plot(x, y)
plt.show()
