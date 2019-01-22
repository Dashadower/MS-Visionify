from src.main import MacroController

macro = MacroController()
macro.terrain_analyzer.load("lachelin_bonsek_2.platform")
macro.terrain_analyzer.calculate_navigation_map()
while True:
    data = macro.loop()
    print(data)
