import json
import os

from gpterminator import Choice
from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate, generateFolderIfNotExists


class SummarizeTypeAgent(Agent):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'summarize-type'
        self.setToolsAndExamples('agents/' + self.agent_name + '/tools')
        self.apply_function_handler = applyFunctionHandler



    def getPromptFolder(self):
        return 'agents/' + self.agent_name + '/prompts'


    def wasSuccessful(self):
        return Choice.hasOneFunctionCall(self.gpterminator.choices)


    def runPrompt(self, type_=None):
        if type_:
            self.generateAllPrompts(type_)

            with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
                prompt = file.read()

            self.gpterminator.getResponse(prompt)

        else:
            print("Please provide a type as an additional argument")


    def generateAllPrompts(self, type_):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'
        generateFolderIfNotExists(folder_name_generated)

        # convert type_ to a string
        type_ = str(type_)

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'type_representation': str(type_)
        })
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def handleFunction(self, function_name, argument_dict):
        if 'summarize_type' == function_name:
            self.summarized_types.append(argument_dict)
            return

        print(f"Function {function_name} not found")

    def resetSummary(self):
        self.summarized_types = []


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
