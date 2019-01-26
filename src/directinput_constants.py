# -*- coding:utf-8 -*-
# IMPORTANT!!! Arrow keys are default bound to numpad 4,6,2,8. Disable numlock befure use!!!!!
# If keyboard input does not work, run as admin
# http://www.flint.jp/misc/?q=dik&lang=en DirectInput Key Codes


DIK_1 = 0x02
DIK_2 = 0x03
DIK_3 = 0x04
DIK_4 = 0x05
DIK_5 = 0x06
DIK_6 = 0x07
DIK_7 = 0x08
DIK_8 = 0x08
DIK_9 = 0x0A
DIK_0 = 0x0B

DIK_A = 0x1E
DIK_B = 0x30
DIK_C = 0x2E
DIK_D = 0x20
DIK_E = 0x12
DIK_F = 0x21
DIK_G = 0x22
DIK_H = 0x23
DIK_I = 0x17
DIK_J = 0x24
DIK_K = 0x25
DIK_L = 0x26
DIK_M = 0x32
DIK_N = 0x31
DIK_O = 0x18
DIK_P = 0x19
DIK_Q = 0x10
DIK_R = 0x13
DIK_S = 0x1F
DIK_T = 0x14
DIK_U = 0x16
DIK_V = 0x2F
DIK_W = 0x11
DIK_X = 0x2D
DIK_Y = 0x15
DIK_Z = 0x2c

DIK_COMMA = 0x33

DIK_LEFT = 0xCB
DIK_RIGHT = 0xCD
DIK_UP = 0xC8
DIK_DOWN = 0xD0

DIK_ALT = 0xB8
DIK_SPACE = 0x39

DIK_NUMLOCK = 0x45

DIK_LCTRL = 0x9D

DIK_RMENU = 0xB8 # Right Alt button (Kor/En)

DIK_RETURN = 0x1C

keysym_map = {  # tkinter event keysym to dik key code coversion table
    "ALT_L":DIK_ALT,
    "CONTROL_L": DIK_LCTRL,
    "space": DIK_SPACE,
    "comma": DIK_COMMA,
    "a": DIK_A,
    "b": DIK_B,
    "c": DIK_C,
    "d": DIK_D,
    "e": DIK_E,
    "f": DIK_F,
    "g": DIK_G,
    "h": DIK_H,
    "i": DIK_I,
    "j": DIK_J,
    "k": DIK_K,
    "l": DIK_L,
    "m": DIK_M,
    "n": DIK_N,
    "o": DIK_O,
    "p": DIK_P,
    "q": DIK_Q,
    "r": DIK_R,
    "s": DIK_S,
    "t": DIK_T,
    "u": DIK_U,
    "v": DIK_V,
    "w": DIK_W,
    "x": DIK_X,
    "y": DIK_Y,
    "z": DIK_Z,
    "1": DIK_1,
    "2": DIK_2,
    "3": DIK_3,
    "4": DIK_4,
    "5": DIK_5,
    "6": DIK_6,
    "7": DIK_7,
    "8": DIK_8,
    "9": DIK_9,
    "0": DIK_0
}
