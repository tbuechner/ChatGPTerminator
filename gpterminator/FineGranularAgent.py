import json
import os

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate


class FineGranularAgent(Agent):
    def __init__(self, gpterminator, application_name):
        super().__init__(gpterminator)
        self.application_name = application_name

    def init(self):
        self.setToolsAndExamples('agents/fine-granular')
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


