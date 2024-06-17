import json
import os

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate


class TextualDiffAgent(Agent):

    def __init__(self, gpterminator, application_name):
        super().__init__(gpterminator)
        self.application_name = application_name
        self.agent_name = 'textual-diff'


    def init(self):
        self.setToolsAndExamples('agents/' + self.agent_name + '-tools')
        self.apply_function_handler = applyFunctionHandler
        self.generateAllPrompts()


    def getPromptFolder(self):
        return 'agents/' + self.agent_name + '-prompts'

    def getPromptApplicationFolder(self):
        return self.getPromptFolder() + '/' + self.application_name


    def runPrompt(self):
        with open(self.getPromptApplicationFolder() + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)


    def generateAllPrompts(self):
        for dir in os.listdir(self.getPromptFolder()):
            if os.path.isdir(os.path.join(self.getPromptFolder(), dir)):
                folder_name_generated = self.getPromptFolder() + '/' + dir + '/generated'
                if os.path.exists(folder_name_generated):
                    os.system("rm -r " + folder_name_generated)

                # create folder folder_name_generated
                os.mkdir(folder_name_generated)

                # load content of file types.json into the variable types
                with open(self.getPromptFolder() + '/' + dir + '/types.json', 'r') as file:
                    types = json.load(file)

                rendered = renderTemplate(self.getPromptFolder() + '/types-template.md', types)
                with open(os.path.join(folder_name_generated, "types.md"), "w") as new_file:
                    new_file.write(rendered)

                rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', None, dir)
                with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
                    new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict, types):
        if 'add_type' == function_name:
            for type_ in types:
                if type_['name'] == argument_dict['name']:
                    print(f"Type with name {argument_dict['name']} already exists")
                    return
            print(f"Adding type with name {argument_dict['name']}")
            types.append(argument_dict)
            return

        if 'add_attribute' == function_name:
            for type_ in types:
                if type_['name'] == argument_dict['typeName']:
                    type_attributes = type_['attributes']
                    type_attributes.append(argument_dict['attribute'])
                    print(f"Adding attribute with name {argument_dict['attribute']['name']} to type {argument_dict['typeName']}")
                    return
            print(f"Type with name {argument_dict['typeName']} does not exist")
            return

        if 'delete_attribute' == function_name:
            for type_ in types:
                if type_['name'] == argument_dict['typeName']:
                    type_attributes = type_['attributes']
                    for i, attribute in enumerate(type_attributes):
                        if attribute['name'] == argument_dict['attributeName']:
                            print(f"Deleting attribute with name {argument_dict['attributeName']} from type {argument_dict['typeName']}")
                            type_attributes.pop(i)
                            return
            print(f"Attribute with name {argument_dict['attributeName']} does not exist in type {argument_dict['typeName']}")

        if 'delete_type' == function_name:
            for i, type in enumerate(types):
                if type['name'] == argument_dict['name']:
                    types.pop(i)
                    print(f"Deleting type with name {argument_dict['name']}")
                    return
            print(f"Type with name {argument_dict['name']} does not exist")
            return

        print(f"Function {function_name} not found")


def applyFunctionHandler(self, function_name, arguments):
    with open(self.getPromptApplicationFolder() + '/types.json', 'r') as file:
        types = json.load(file)

    print("Applying function calls")
    for argument in arguments:
        argument_dict = json.loads(argument)
        print(f"Function: {function_name}")
        self.handleFunction(function_name, argument_dict, types)

    # write the types to the types.json file
    with open(self.getPromptApplicationFolder() + '/types.json', 'w') as file:
        json.dump(types, file, indent=4)

    self.generateAllPrompts()

    self.gpterminator.msg_hist = self.gpterminator.msg_hist[:1]
    self.gpterminator.prompt_count = 0

    print("Session has been reset. You can now run the prompt again.")


