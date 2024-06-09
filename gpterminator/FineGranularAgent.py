import json
import os

import jsonschema

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate


class FineGranularAgent(Agent):
    def __init__(self, gpterminator, application_name):
        super().__init__(gpterminator)
        self.application_name = application_name

    def init(self):
        self.setToolsAndExamples('agents/fine-granular')
        self.apply_function_handler = applyFunctionHandler
        self.generateAllPrompts()


    def runPrompt(self):
        with open(self.getPromptApplicationFolder() + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)


    def getPromptFolder(self):
        return 'agents/fine-granular/prompts'


    def getPromptApplicationFolder(self):
        return 'agents/fine-granular/prompts/' + self.application_name


    def generateAllPrompts(self):
        for dir in os.listdir(self.getPromptFolder()):
            if os.path.isdir(os.path.join(self.getPromptFolder(), dir)):
                folder_name_generated = self.getPromptFolder() + '/' + dir + '/generated'
                if os.path.exists(folder_name_generated):
                    os.system("rm -r " + folder_name_generated)

                # create folder folder_name_generated
                os.mkdir(folder_name_generated)

                rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', None, dir)
                with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
                    new_file.write(rendered)

    def handleFunction(self, function_name, argument_dict, types):
        print(f"Function: {function_name}")
        print(f"Arguments: {argument_dict}")
        print(f"Types: {types}")

        # iterate over self.gpterminator.tools
        for tool in self.gpterminator.tools:
            if tool['function']['name'] == function_name:
                print(f"Tool with name {function_name} found")
                schema_as_string = tool['function']['parameters']
                schema = json.loads(schema_as_string)
                try:
                    jsonschema.validate(instance=argument_dict, schema=schema)
                    print("JSON object is valid")
                except jsonschema.exceptions.ValidationError as ve:
                    print("JSON object is not valid.")
                break

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

def applyFunctionHandler(self, function_name, arguments):
    with open(self.getPromptApplicationFolder() + '/types-detailed.json', 'r') as file:
        types = json.load(file)

    print("Applying function calls")
    for argument in arguments:
        argument_dict = json.loads(argument)
        print(f"Function: {function_name}")
        self.handleFunction(function_name, argument_dict, types)

    # write the types to the types.json file
    with open(self.getPromptApplicationFolder() + '/types-detailed.json', 'w') as file:
        json.dump(types, file, indent=4)

    self.generateAllPrompts()

    self.gpterminator.msg_hist = self.gpterminator.msg_hist[:1]
    self.gpterminator.prompt_count = 0

    print("Session has been reset. You can now run the prompt again.")
