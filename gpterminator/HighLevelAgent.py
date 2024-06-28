import json
import os

from gpterminator import Choice
from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate, generateFolderIfNotExists, createEmptyFileIfNotExists


class HighLevelAgent(Agent):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'high-level'
        self.setToolsAndExamples('agents/' + self.agent_name + '/tools')
        self.apply_function_handler = applyFunctionHandler


    def getPromptFolder(self):
        return 'agents/' + self.agent_name + '/prompts'


    def wasSuccessful(self):
        return Choice.isSuccessful(self.gpterminator.choices, "The current data model meets the requirements of the application.")


    def runPrompt(self, additional_args=None):
        self.generateAllPrompts()
        with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)

        self.checkIfPromptAgain(additional_args)


    def generateAllPrompts(self):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'

        types_file_name = 'applications/' + self.gpterminator.application_name + '/types-high-level.json'

        createEmptyFileIfNotExists(types_file_name)

        with open(types_file_name, 'r') as file:
            types = json.load(file)

        rendered = renderTemplate(self.getPromptFolder() + '/types-high-level-template.md', {
            'types': types,
            'application_name': self.gpterminator.application_name
        })
        with open(os.path.join(folder_name_generated, "types-high-level.md"), "w") as new_file:
            new_file.write(rendered)

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'application_name': self.gpterminator.application_name,
            'high_level_data_model_is_empty': len(types) == 0,
        })
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


def applyFunctionHandler(self, function_name, argument):
    with open('applications/' + self.gpterminator.application_name + '/types-high-level.json', 'r') as file:
        types = json.load(file)

    argument_dict = json.loads(argument)
    print(f"Applying function: {function_name}")
    self.handleFunction(function_name, argument_dict, types)

    # write the types to the types.json file
    with open('applications/' + self.gpterminator.application_name + '/types-high-level.json', 'w') as file:
        json.dump(types, file, indent=4)
