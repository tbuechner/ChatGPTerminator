import json
import os

from Chain import Chain
from Utils import renderTemplate, generateFolderIfNotExists


class SearchCombineFiltersChain(Chain):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.chain_name = 'search-combine-filters'
        self.setToolsAndExamples('chains/' + self.chain_name + '/tools')
        self.apply_function_handler = applyFunctionHandler


    def getPromptFolder(self):
        return 'chains/' + self.chain_name + '/prompts'


    def runPrompt(self, additional_args=None):
        self.generateAllPrompts()
        with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        self.gpterminator.getResponse(prompt)


    def generateAllPrompts(self):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'application_name': self.gpterminator.application_name
        })
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict):
        print(f"Handling function: {function_name} with argument: {argument_dict}")


def applyFunctionHandler(self, function_name, argument):
    argument_dict = json.loads(argument)
    print(f"Applying function: {function_name}")
    self.handleFunction(function_name, argument_dict)
