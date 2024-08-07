import json
import os

import jsonschema

import Choice
from Chain import Chain
from Utils import renderTemplate, generateFolderIfNotExists, createEmptyFileIfNotExists


class FineGranularTypesChain(Chain):
    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.chain_name = 'fine-granular-types'
        self.setToolsAndExamples('chains/' + self.chain_name + '/tools')
        self.apply_function_handler = applyFunctionHandler


    def runPrompt(self, additional_args=None):
        self.generateAllPrompts()
        with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)

        self.checkIfPromptAgain(additional_args)

    def wasSuccessful(self):
        return Choice.isSuccessful(self.gpterminator.choices, "The types of the detailed data model meet the requirements of the application.")


    def getPromptFolder(self):
        return 'chains/' + self.chain_name + '/prompts'


    def generateAllPrompts(self):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'

        types_detailed_file_name = 'applications/' + self.gpterminator.application_name + '/types-detailed.json'
        createEmptyFileIfNotExists(types_detailed_file_name)

        with open(types_detailed_file_name, 'r') as file:
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
            argument_dict['attributes'] = []
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


def applyFunctionHandler(self, function_name, argument):
    with open('applications/' + self.gpterminator.application_name + '/types-detailed.json', 'r') as file:
        types = json.load(file)

    argument_dict = json.loads(argument)
    print(f"Applying function {function_name}")
    self.handleFunction(function_name, argument_dict, types)

    # write the types to the types.json file
    with open('applications/' + self.gpterminator.application_name + '/types-detailed.json', 'w') as file:
        json.dump(types, file, indent=4)

    self.generateAllPrompts()
