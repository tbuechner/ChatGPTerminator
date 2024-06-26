import json
import os

import jsonschema

from gpterminator.Agent import Agent
from gpterminator.Utils import renderTemplate, generateFolderIfNotExists


class FineGranularAgent(Agent):
    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.agent_name = 'fine-granular'


    def runPrompt(self, additional_args=None):
        pass
