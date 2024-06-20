import json
import os

import jsonschema

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate, generateFolderIfNotExists


class FineGranularTypesAgent(Agent):
    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'fine-granular-types'
        self.setToolsAndExamples('agents/' + self.agent_name + '/tools')
        self.apply_function_handler = applyFunctionHandler


    def runPrompt(self, additional_args=None):
        self.generateAllPrompts()
        with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)


    def getPromptFolder(self):
        return 'agents/' + self.agent_name + '/prompts'


    def generateAllPrompts(self):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'
        generateFolderIfNotExists(folder_name_generated)

        with open('applications/' + self.gpterminator.application_name + '/types-detailed.json', 'r') as file:
            types_detailed = json.load(file)
        for type_ in types_detailed:
            type_.pop('attributes', None)
        with open(folder_name_generated + '/types-detailed-only-types.json', 'w') as file:
            json.dump(types_detailed, file, indent=4)

        with open('applications/' + self.gpterminator.application_name + '/types-high-level.json', 'r') as file:
            types = json.load(file)

        rendered = renderTemplate(self.getPromptFolder() + '/types-high-level-template.md', {
            'types': types,
            'application_name': self.gpterminator.application_name
        })
        with open(os.path.join(folder_name_generated, "types-high-level.md"), "w") as new_file:
            new_file.write(rendered)

        with open('applications/' + self.gpterminator.application_name + '/prompt-detailed.md', 'r') as file:
            prompt_detailed = file.read()

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'application_name': self.gpterminator.application_name,
            'prompt_detailed': prompt_detailed
        })
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict, types):
        print(f"Function: {function_name}")
        # print(f"Arguments: {argument_dict}")
        # print(f"Types: {types}")

        if not self.validateSchema(argument_dict, function_name):
            return

        if 'add_type' == function_name:
            for type_ in types:
                if type_['internalName'] == argument_dict['internalName']:
                    print(f"Type with name {argument_dict['internalName']} already exists")
                    return
            print(f"Adding type with name {argument_dict['internalName']}")
            types.append(argument_dict)
            return

        if 'remove_type' == function_name:
            for type_ in types:
                if type_['internalName'] == argument_dict['internalName']:
                    print(f"Removing type with name {argument_dict['internalName']}")
                    types.remove(type_)
                    return
            print(f"Type with name {argument_dict['internalName']} not found")
            return


def applyFunctionHandler(self, function_name, arguments):
    with open('applications/' + self.gpterminator.application_name + '/types-detailed.json', 'r') as file:
        types = json.load(file)

    print("Applying function calls")
    for argument in arguments:
        argument_dict = json.loads(argument)
        print(f"Function: {function_name}")
        self.handleFunction(function_name, argument_dict, types)

    # write the types to the types.json file
    with open('applications/' + self.gpterminator.application_name + '/types-detailed.json', 'w') as file:
        json.dump(types, file, indent=4)

    self.generateAllPrompts()
