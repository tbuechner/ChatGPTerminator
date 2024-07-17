import json
import os

import Choice
from Chain import Chain
from Utils import renderTemplate, generateFolderIfNotExists


class SummarizeAttributeChain(Chain):

    def __init__(self, gpterminator, summarized_types):
        super().__init__(gpterminator)
        self.chain_name = 'summarize-attribute'
        self.setToolsAndExamples('chains/' + self.chain_name + '/tools')
        self.apply_function_handler = applyFunctionHandler
        self.summarized_types = summarized_types


    def getPromptFolder(self):
        return 'chains/' + self.chain_name + '/prompts'


    def wasSuccessful(self):
        return Choice.hasOneFunctionCall(self.gpterminator.choices)


    def runPrompt(self, attribute_and_type_index=None):
        if attribute_and_type_index is not None:
            attribute = attribute_and_type_index[0]
            self.type_index = attribute_and_type_index[1]
            self.attribute = attribute

            self.generateAllPrompts(attribute)

            with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
                prompt = file.read()

            self.gpterminator.getResponse(prompt)

        else:
            print("Please provide an attribute as an additional argument")


    def generateAllPrompts(self, attribute):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'attribute_representation': str(attribute)
        })
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict):
        if 'summarize_attribute' == function_name:
            attributes = self.summarized_types[self.type_index].get('attributes')
            if attributes is None:
                attributes = []
                self.summarized_types[self.type_index]['attributes'] = attributes
            argument_dict['internalAttributeName'] = self.attribute['internalName']
            attributes.append(argument_dict)
            return

        print(f"Function {function_name} not found")


    def saveSummary(self):
        file_name = self.getSummarizedFileName()
        with open(file_name, "w") as new_file:
            new_file.write(json.dumps(self.summarized_types, indent=4))


    def getSummarizedFileName(self):
        return 'applications/' + self.gpterminator.application_name + '/types-summarized-high-level.json'


def applyFunctionHandler(self, function_name, argument):
    argument_dict = json.loads(argument)
    print(f"Applying function: {function_name}")
    self.handleFunction(function_name, argument_dict)
