import json
import os

import Choice
from Chain import Chain
from Utils import renderTemplate, generateFolderIfNotExists


class SummarizeTypeChain(Chain):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.chain_name = 'summarize-type'
        self.setToolsAndExamples('chains/' + self.chain_name + '/tools')
        self.apply_function_handler = applyFunctionHandler
        self.summarized_types = []


    def getPromptFolder(self):
        return 'chains/' + self.chain_name + '/prompts'


    def wasSuccessful(self):
        return Choice.hasOneFunctionCall(self.gpterminator.choices)


    def runPrompt(self, type_=None):
        if type_:
            self.generateAllPrompts(type_)
            self.type_ = type_

            with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
                prompt = file.read()

            self.gpterminator.getResponse(prompt)

        else:
            print("Please provide a type as an additional argument")


    def generateAllPrompts(self, type_):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'type_representation': str(type_)
        })
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict):
        if 'summarize_type' == function_name:
            argument_dict['internalTypeName'] = self.type_['internalName']
            self.summarized_types.append(argument_dict)
            return

        print(f"Function {function_name} not found")


def applyFunctionHandler(self, function_name, argument):
    argument_dict = json.loads(argument)
    print(f"Applying function: {function_name}")
    self.handleFunction(function_name, argument_dict)
