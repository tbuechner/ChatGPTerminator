import json
import os

import jsonschema

import Choice
from Chain import Chain
from Utils import renderTemplate, generateFolderIfNotExists, createEmptyFileIfNotExists


class ExamplePagesReferencesChain(Chain):
    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.chain_name = 'example-pages-references'
        self.setToolsAndExamples('chains/' + self.chain_name + '/tools')
        self.apply_function_handler = applyFunctionHandler


    def runPrompt(self, additional_args=None):
        self.generateAllPrompts()

        with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)

    def getPromptFolder(self):
        return 'chains/' + self.chain_name + '/prompts'


    def generateAllPrompts(self):
        types_detailed_file_name = 'applications/' + self.gpterminator.application_name + '/types-detailed.json'

        with open(types_detailed_file_name, 'r') as file:
            types_detailed = json.load(file)

        for type_ in types_detailed:
            indexes_to_remove = []
            for attribute in type_['attributes']:
                if attribute['constraint']['attributeType'] != 'reference':
                    indexes_to_remove.append(type_['attributes'].index(attribute))

            # remove in reverse order
            for index in sorted(indexes_to_remove, reverse=True):
                del type_['attributes'][index]

        file_name = self.getExamplePagesFileName()

        with open(file_name, 'r') as file:
            existing_pages = json.load(file)

        for type_ in existing_pages:
            for page in type_['pages']:

                original_list = page['attributes']

                for x in original_list[:]:  # Iterate over a copy of the list
                    if 'id' not in x and 'ids' not in x:
                        original_list.remove(x)

                if len(original_list) == 0:
                    del page['attributes']


        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'application_name': self.gpterminator.application_name,
            'types_detailed': json.dumps(types_detailed),
            'existing_pages': json.dumps(existing_pages)
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

        if 'set_references' == function_name:
            for type_ in pages:
                if type_['typeInternalName'] == argument_dict['typeInternalName']:
                    for page in type_['pages']:
                        if page['pageName'] == argument_dict['pageName']:
                            for attribute in argument_dict['attributes']:
                                attribute_name = attribute['name']
                                attribute_already_exists = False
                                for existing_attribute in page['attributes']:
                                    if existing_attribute['name'] == attribute_name:
                                        print("Attribute already exists")
                                        attribute_already_exists = True
                                        break

                                if not attribute_already_exists:
                                    print(f"Adding attribute {attribute_name} to page {page['pageName']}")
                                    page['attributes'].append(attribute)


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
