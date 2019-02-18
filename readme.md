# MacroStory: OpenCV based KMS MapleStory automation on Python3
This projects aims to create a intelligent automated bot for KMS MapleStory with the character Demon Avenger. 
The bot uses OpenCV to find features from the game screen and use DirectInput emulation to interact
with the game.

### *What's the difference from just normal "macros"?*
* The "bot" does not use *any* prerecorded keypress sequences to control the character, unlike a key recorded macro.
* The "bot" intelligently plans a path using terrain information of a given map, enabling the bot to be more efficient and
  less susceptible to anti-bot detection techniques, like static pattern detection and movement frequency analysis.
* The "bot" can be easily integrated into any map since all the information it needs are the start and end points of platforms.

### *How does it work?*
 It's actually very simple. The bot uses image processing to extract player coordinates from the on-screen minimap. On
 the regular version, it maintains a tree structure of the platforms, selecting a destination platform based on least-visited-first
 strategy. On Version 2, it will use A* to construct a path. After that, it's just a matter of using skills at the right intervals.

## prerequisites:
* OpenCV-Python
* imutils
* numpy
* pywin32
* PIL(Pillow)
* tensorflow
* Keras
* pythoncom, pyHook (optional, for debugging)

### Note of regard to code users
*Commercial usage of the following code is free of will, but discouraged.* This project was not intended to be commercialized, and was
only for research purposes and proof-of-concept. Any malicious uses of the following code can result in
Nexon reenforcing anti-bot features which will render this bot and future improvements useless.
