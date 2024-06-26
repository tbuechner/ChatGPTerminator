import json
from pathlib import Path

from gpterminator.Utils import get_file_name


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

    def save(self, save_path):
        file_name = f"{get_file_name(save_path)}-text.md"
        with open(Path(save_path) / file_name, "w") as f:
            f.write(self.content)


    def getMsgForHistory(self):
        return {"role": "assistant", "content": self.content}



class FunctionCall(Choice):
    def __init__(self, id, function_name, arguments):
        super().__init__(id)
        self.function_name = function_name
        self.arguments = arguments

    def __str__(self):
        return "FunctionCall: " + self.function_name + " " + str(self.arguments)

    def __repr__(self):
        return "FunctionCall: " + self.function_name + " " + str(self.arguments)

    def save(self, save_path):
        file_name = f"{get_file_name(save_path)}-{self.function_name}.json"
        with open(Path(save_path) / file_name, "w") as f:
            json_object = json.loads(self.arguments)
            json.dump(json_object, f, indent=4)


    def getMsgForHistory(self):
        return {"role": "assistant", "content": None, "function_call": self.function_name, "arguments": self.arguments}


def addTextualChoice(choices, id, content):
    for c in choices:
        if c.id == id:
            c.content += content
            return content
    choices.append(Textual(id, content))
    return content

def addFunctionCall(choices, id, function_name, arguments):
    if function_name is not None:
        choices.append(FunctionCall(id, function_name, arguments))
        return f"Function call {function_name}"
    else:
        # get last element of choices
        last = choices[-1]
        last.arguments += arguments
        return arguments

def getFunctionCalls(choices):
    return [c for c in choices if isinstance(c, FunctionCall)]

def hasTextualChoice(choices):
    return any(isinstance(c, Textual) for c in choices)