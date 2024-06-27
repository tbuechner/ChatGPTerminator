import json
import os

from gpterminator import Choice
from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate, generateFolderIfNotExists


class CompareAgent(Agent):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'compare'
        self.setToolsAndExamples('agents/' + self.agent_name + '/tools')


    def getPromptFolder(self):
        return 'agents/' + self.agent_name + '/prompts'


    def runPrompt(self, additional_args=None):
        self.generateAllPrompts()
        with open('applications/' + self.gpterminator.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        self.gpterminator.getResponse(prompt)


    def generateAllPrompts(self):
        folder_name_generated = 'applications/' + self.gpterminator.application_name + '/generated'
        generateFolderIfNotExists(folder_name_generated)

        high_level_file_name = 'applications/' + self.gpterminator.application_name + '/types-high-level.json'
        with open(high_level_file_name, 'r') as file:
            types = json.load(file)

        summarized_file_name = 'applications/' + self.gpterminator.application_name + '/types-summarized-high-level.json'
        with open(summarized_file_name, 'r') as file:
            types_summarized = json.load(file)

        rendered = renderTemplate(self.getPromptFolder() + '/types-high-level-template.md', {
            'types': types
        })
        with open(os.path.join(folder_name_generated, "types-high-level.md"), "w") as new_file:
            new_file.write(rendered)

        rendered_summarized = renderTemplate(self.getPromptFolder() + '/types-high-level-template.md', {
            'types': types_summarized
        })
        with open(os.path.join(folder_name_generated, "types-summarized-high-level.md"), "w") as new_file:
            new_file.write(rendered)

        rendered = renderTemplate(self.getPromptFolder() + '/prompt-template.md', {
            'application_name': self.gpterminator.application_name,
            'original_data_model': rendered,
            'reverse_engineered_data_model': rendered_summarized
        })
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)
