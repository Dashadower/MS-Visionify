import src.macro_script, time
time.sleep(2)
macro = src.macro_script.MacroController()
macro.terrain_analyzer.load("본색을 드러내는 곳 2.platform")
macro.terrain_analyzer.calculate_navigation_map()
while True:
    data = macro.loop()
    print(data)
