import json
import os

import jsonschema

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate, generateFolderIfNotExists


class FineGranularAgent(Agent):
    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'fine-granular'
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

        if (
                'add_boolean_attribute' == function_name or
                'add_date_attribute' == function_name or
                'add_long_text_attribute' == function_name or
                'add_number_attribute' == function_name or
                'add_number_enumeration_attribute' == function_name or
                'add_reference_attribute' == function_name or
                'add_rich_string_attribute' == function_name or
                'add_string_attribute' == function_name or
                'add_string_enumeration_attribute' == function_name

        ):
            for type_ in types:
                if type_['internalName'] == argument_dict['internalTypeName']:
                    if 'attributes' not in type_:
                        type_['attributes'] = []
                    for attribute in type_['attributes']:
                        if attribute['internalName'] == argument_dict['internalName']:
                            print(f"Attribute with name {argument_dict['internalName']} already exists")
                            return
                    print(f"Adding attribute with name {argument_dict['internalName']} to type {argument_dict['internalTypeName']}")
                    del argument_dict['internalTypeName']
                    type_['attributes'].append(argument_dict)
                    return
            print(f"Type with name {argument_dict['typeName']} does not exist")
            return

        if 'remove_type' == function_name:
            for type_ in types:
                if type_['internalName'] == argument_dict['internalName']:
                    print(f"Removing type with name {argument_dict['internalName']}")
                    types.remove(type_)
                    return
            print(f"Type with name {argument_dict['internalName']} not found")
            return

        if 'remove_attribute' == function_name:
            for type_ in types:
                if type_['internalName'] == argument_dict['internalTypeName']:
                    for attribute in type_['attributes']:
                        if attribute['internalName'] == argument_dict['internalName']:
                            print(f"Removing attribute with name {argument_dict['internalName']} from type {argument_dict['internalTypeName']}")
                            type_['attributes'].remove(attribute)
                            return
                    print(f"Attribute with name {argument_dict['internalName']} not found in type {argument_dict['internalTypeName']}")
                    return
            print(f"Type with name {argument_dict['internalTypeName']} not found")
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
