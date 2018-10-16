
#Macro script parser
#Macro script format
"""
Script file Format
constants:
CPOS_X                current player Y position
CPOS_Y                current player Y position
define x y            replace x with y
------------------------
setattack float_interval float_duration const_DIK_KEYCODE
#set attack interval to float duration with key DIK_KEYCODE
------------------------
setpath_x int_x1 int_x2
#move from path x1 to x2
------------------------
keydown const_DIK_KEYCODE
#press DIK_KEYCODE down
------------------------
keyup const_DIK_KEYCODE
#press DIK_KEYCODE back up
------------------------
singlepress float_duration const_DIK_KEYCODE
#press DIK_KEYCODE for duration seconds
------------------------
wait float_duration
#time.sleep(duration)
------------------------
#Syntax tokens
#Token types:
DELIMETER
space induced delimeter (expression separator)
newline(\n) (statement separator)
tab(\t) (block separator/code level separator)
TOKEN                        STATE
DELIM_SPACE                  PUSH + COUNT
DELIM_SPACE + DELIM_SPACE    POP + RESET
DELIM_TAB                    PUSH
DELIM_ESCAPE_TAB             POP + RESET
"""
commands = {
    "setattack":[float, float, str],
    "setpath": [int, int],
    "keydown": [str],
    "keyup": [str],
    "singlepress": [str],
    "wait": [float]
}


class FiniteStateAutomata:
    def __init__(self):
        self.raw_stack = []
        self.lexed_stack = []
        self.parsed_stack = []

    def lexical_analyzer(self, inp_string, rule):
        pass

    def semantic_analyzer(self, ):
        pass
class ScriptReader:
    def __init__(self, filedir):
        self.filedir = filedir
        self.unparsed_lines = []
        self.parsed_lines = []
        self.definitions = []
    def preprocess(self):
        self.unparsed_lines = []
        self.definitions = []
        with open(self.filedir, "r") as f:
            for line in f.readlines():
                line = line.strip("\n")
                delimeted = line.split(" ")
                if delimeted[0] == "define":
                    self.definitions.append([delimeted[1], delimeted[2]])
                else:
                    self.unparsed_lines.append(delimeted)


        for line in self.unparsed_lines:
            if line[0] == "define":
                self.definitions.append([line[1], line[2]])
        print(self.definitions)
        for line in self.unparsed_lines:
            tmp_arr = []
            cmd = None
            for index, value in enumerate(line):
                if index == 0 and value in commands.keys():
                    tmp_arr.append(value)
                    cmd = value
                    continue
                if index != 0:
                    for definition in self.definitions:
                        if value == definition[0]:
                            value = definition[1]
                    value = commands[cmd][index-1](value)
                    tmp_arr.append(value)
            self.parsed_lines.append(tmp_arr)




if __name__ == "__main__":
    parser = ScriptReader("test_macro1.macro")
    parser.preprocess()
    print(parser.parsed_lines)