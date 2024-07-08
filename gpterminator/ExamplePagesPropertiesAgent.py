import json
import os

import jsonschema

import Choice
from Agent import Agent
from Utils import renderTemplate, generateFolderIfNotExists, createEmptyFileIfNotExists


class ExamplePagesPropertiesAgent(Agent):
    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'example-pages-properties'
        self.setToolsAndExamples('agents/' + self.agent_name + '/tools')
        self.apply_function_handler = applyFunctionHandler


    def runPrompt(self, additional_args=None):
        type_index = additional_args[0] if additional_args else None

        if type_index is not None:
            type_index = int(type_index)

            types_detailed_file_name = 'applications/' + self.gpterminator.application_name + '/types-detailed.json'

            with open(types_detailed_file_name, 'r') as file:
                types_detailed = json.load(file)

            type_ = types_detailed[type_index]

            file_name = self.getExamplePagesFileName()
            createEmptyFileIfNotExists(file_name)
            with open(file_name, 'r') as file:
                example_pages = json.load(file)

            type_internal_name = type_['internalName']

            existing_type = self.findType(type_internal_name, example_pages)
            existing_pages = existing_type['pages']

            if len(existing_pages) < 10:
                self.generateAllPrompts(type_, existing_type, existing_pages)

                with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
                    prompt = file.read()

                # print("prompt: " + prompt)

                self.gpterminator.getResponse(prompt)
            else:
                print(f"Maximum number of pages reached for type {type_internal_name}")
                return
        else:
            print("Please provide a type index as an additional argument")
            return


    def getPromptFolder(self):
        return 'agents/' + self.agent_name + '/prompts'


    def generateAllPrompts(self, type_, existing_type, existing_pages):

        # remove reference attributes
        indexes_to_remove = []
        for attribute in type_['attributes']:
            if attribute['constraint']['attributeType'] == 'reference':
                indexes_to_remove.append(type_['attributes'].index(attribute))

        # remove in reverse order
        for index in sorted(indexes_to_remove, reverse=True):
            del type_['attributes'][index]

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'application_name': self.gpterminator.application_name,
            'type_detailed': json.dumps(type_),
            'pages_exist': len(existing_pages) > 0,
            'existing_pages': json.dumps(existing_pages),
            'number_of_pages_to_generate': 10 - len(existing_pages) if len(existing_pages) < 10 else 0,
        })

        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict, pages):
        print(f"Function: {function_name}")
        # print(f"Arguments: {argument_dict}")
        # print(f"Types: {types}")

        if not self.validateSchema(argument_dict, function_name):
            return

        if 'add_page' == function_name:
            type_internal_name = argument_dict['typeInternalName']
            type_ = self.findType(type_internal_name, pages)

            existing_pages = type_['pages']
            existing_ids = []
            if len(existing_pages) == 10:
                print(f"Maximum number of pages reached for type {type_internal_name}")
                return
            for existing_page in existing_pages:
                existing_ids.append(existing_page['id'])
                if existing_page['pageName'] == argument_dict['pageName']:
                    print(f"Page with name {argument_dict['internalName']} already exists")
                    return
            # find the max id in existing_ids
            if len(existing_ids) == 0:
                max_id = 0
            else:
                max_id = max(existing_ids)
            print(f"Adding page with name {argument_dict['pageName']} to type {type_internal_name}")
            existing_pages.append({
                'id': max_id + 1,
                'pageName': argument_dict['pageName'],
                'attributes': argument_dict['attributes']
            })
            return



    def findType(self, type_internal_name, pages):
        for type_ in pages:
            if type_['typeInternalName'] == type_internal_name:
                return type_

            print(f"Type with internal name {type_internal_name} not found, appending")

        type_ = {
            'typeInternalName': type_internal_name,
            'pages': []
        }
        pages.append(type_)
        return type_


    def getExamplePagesFileName(self):
        return 'applications/' + self.gpterminator.application_name + '/example-pages.json'


def applyFunctionHandler(self, function_name, argument):
    file_name = self.getExamplePagesFileName()

    with open(file_name, 'r') as file:
        pages = json.load(file)

    argument_dict = json.loads(argument)
    print(f"Applying function {function_name}")
    self.handleFunction(function_name, argument_dict, pages)

    with open(file_name, 'w') as file:
        json.dump(pages, file, indent=4)
