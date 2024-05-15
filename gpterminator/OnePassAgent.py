import json
import os

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate


class OnePassAgent(Agent):
    def __init__(self, gpterminator, application_name):
        super().__init__(gpterminator)
        self.application_name = application_name

    def init(self):
        self.setToolsAndExamples('agents/one-pass')
        self.generateAllPrompts()


    def runPrompt(self):
        with open(self.getPromptApplicationFolder() + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)


    def getPromptFolder(self):
        return 'agents/one-pass/prompts'


    def getPromptApplicationFolder(self):
        return 'agents/one-pass/prompts/' + self.application_name


    def generateAllPrompts(self):
        for dir in os.listdir(self.getPromptFolder()):
            if os.path.isdir(os.path.join(self.getPromptFolder(), dir)):
                folder_name_generated = self.getPromptFolder() + '/' + dir + '/generated'
                if os.path.exists(folder_name_generated):
                    os.system("rm -r " + folder_name_generated)

                # create folder folder_name_generated
                os.mkdir(folder_name_generated)

                # load content of file types.json into the variable types
                with open(self.getPromptFolder() + '/' + dir + '/types-high-level.json', 'r') as file:
                    types = json.load(file)

                rendered = renderTemplate(self.getPromptFolder() + '/types-high-level-template.md', types)
                with open(os.path.join(folder_name_generated, "types.md"), "w") as new_file:
                    new_file.write(rendered)

                rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', None, dir)
                with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
                    new_file.write(rendered)

