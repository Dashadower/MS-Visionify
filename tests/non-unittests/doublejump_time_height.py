import matplotlib.pyplot as plt, time
from src.screen_processor import MapleScreenCapturer, StaticImageProcessor
from src.directinput_constants import DIK_ALT, DIK_UP
from src.keystate_manager import KeyboardInputManager

cap = MapleScreenCapturer()
scrp = StaticImageProcessor(cap)
scrp.update_image(set_focus=True)
rect = scrp.get_minimap_rect()

inp = KeyboardInputManager()

start_delay = 0.5
increment = -0.05
plot_data = []
while start_delay > 0:
    scrp.update_image(set_focus=False)
    current_y = scrp.find_player_minimap_marker(rect)[1]
    start_time = time.time()
    inp.single_press(DIK_ALT)
    time.sleep(start_delay)
    inp.single_press(DIK_UP)
    time.sleep(0.01)
    inp.single_press(DIK_UP)
    y_list = []
    while abs(time.time() - start_time) < 3:
        scrp.update_image(set_focus=False)
        y_list.append(scrp.find_player_minimap_marker(rect)[1])
    plot_data.append((round(start_delay, 2), abs(current_y-min(y_list))))
    print("Delay: %f distance: %d"%(round(start_delay, 2), abs(current_y-min(y_list))))
    time.sleep(2)
    start_delay += increment

print(plot_data)
x,y = zip(*plot_data)
plt.scatter(x,y)
plt.show()