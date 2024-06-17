from gpterminator.Agent import Agent


class TextualAgent(Agent):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.setToolsAndExamples('agents/textual')

