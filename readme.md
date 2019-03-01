# MS-Visionify: OpenCV based KMS MapleStory automation on Python3
This projects aims to create a intelligent automated bot for KMS MapleStory with the character Demon Avenger. 
The bot uses OpenCV to find features from the game screen and use DirectInput emulation to interact
with the game.

## 2019.3.1 - No longer being updated because of abuse and personal decisions
 Ms-Visionify was created to attempt to perfectly mimicking a human in a RPG environment. Although I was aware bots were
against the terms of service of the game, I did continue developing the bot, and unfortunately, it has been exploited
for commercial purposes like selling partly and fully compiled versions of the bot. I reconsidered the effects on the
game if this bot becomes well known, and concluded that it's not right to continue the development and fully release the
source so anyone can bot the game. Therefore, I have decided that **no further development will be continued on MS-Visionify.**
However, I will not take any of the source down or the repo itself. Although a short-lived project, it provided valuable
experience in image processing and automation.

KR: MS-Visionify 프로젝트는 "사람을 완전히 모방할수 있는 능력을 가진 봇"을 개발하자는 취지로 시작되었습니다. 개발 시작부터 이런
류의 프로그램은 게임의 이용 약관을 위반한다는 것을 알고 있음에도 불구하고, 계속 개발을 하게 되었습니다. 안타깝게도, 본래의 취지와는 반대로
상업적인 목표로 남용되기 시작되었습니다. 저는 이 프로그램이 대중화되었을때 메이플스토리에 끼치게 될 영향에 대해 다시 생각해보게 되었고, 결론적으로
개발을 계속하는 것과 누구나 사용할수 있게끔 소스를 공개하는 행동은 부정적인 영향밖에 없을거라고 생각했습니다. **MS-Visionify의 개발을 중지하기로 결정했습니다.**
다만 현재까지 공개된 소스와 repository 자체는 삭제하지 않을 예정입니다.

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
* matplotlib (optional, for debugging)

### Note of regard to code users
*Commercial usage of the following code is free of will, but discouraged.* This project was not intended to be commercialized, and was
only for research purposes and proof-of-concept. Any malicious uses of the following code can result in
Nexon reenforcing anti-bot features which will render this bot and future improvements useless.

### To Nexon:
If you have issues with the following code being developed/distributed, please contact me so we can get the issues resolved.

This software is in no way associated with or endorsed by Nexon or any subsidiaries.
