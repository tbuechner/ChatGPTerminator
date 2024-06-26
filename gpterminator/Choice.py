class Choice:
    def __init__(self, id):
        self.id = id


class Textual(Choice):
    def __init__(self, id, content):
        super().__init__(id)
        self.content = content

    def __str__(self):
        return "Textual: " + self.content

    def __repr__(self):
        return "Textual: " + self.content


class FunctionCall(Choice):
    def __init__(self, id, function_name, arguments):
        super().__init__(id)
        self.function_name = function_name
        self.arguments = arguments

    def __str__(self):
        return "FunctionCall: " + self.function_name + " " + str(self.arguments)

    def __repr__(self):
        return "FunctionCall: " + self.function_name + " " + str(self.arguments)


def addTextualChoice(choices, id, content):
    for c in choices:
        if c.id == id:
            c.content += content
            return
    choices.append(Textual(id, content))

def addFunctionCall(choices, id, function_name, arguments):
    if function_name is not None:
        choices.append(FunctionCall(id, function_name, arguments))
    else:
        # get last element of choices
        last = choices[-1]
        last.arguments += arguments

def getFunctionCalls(choices):
    return [c for c in choices if isinstance(c, FunctionCall)]