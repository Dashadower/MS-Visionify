

class LexicalParser:
    def __init__(self, inp_stream, rules):
        self.raw_stream = inp_stream
        self.rules = rules

    def lexer(self):
        for char in self.raw_stream:
            for policy in self.rules:
                if policy[1] == char:
                    current_policy = policy[1]
                else:
                    current_policy = None

                lex_stack = []
                if current_policy:
                    for char2 in self.raw_stream[self.raw_stream.index(char):]:
                        next_policy = None
                        for second_policy in self.rules:
                            if second_policy != current_policy:
                                lex_stack.append(char2)
                            elif second_policy != current_policy and char2 == second_policy[1]:
                                lex_stack.pop(0)
                                lex_stack.remove(char2)
                                lex_stack.append(char2)

    def lookahead(self, inp_str, index, delimeter, lex_rule, *args):
        parsed =  inp_str.split(delimeter)
        if parsed[0] == lex_rule[1]:
            return 0
        else:
            parsed_list = []
            for token in parsed:
                for rule in lex_rule:
                    if token == rule[0]:
                        parsed_list.append(rule[1])
                    if len(parsed_list) >= 1 and parsed_list[-1] == token:
                        parsed_list.pop(-1)

            return parsed_list[-1]
