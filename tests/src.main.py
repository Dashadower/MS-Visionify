from src.main import MacroController

macro = MacroController()
macro.terrain_analyzer.load("mapdata.platform")
macro.terrain_analyzer.calculate_navigation_map()
while True:
    data = macro.loop()
    print(data)
