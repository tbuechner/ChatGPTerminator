from gpterminator.Agent import Agent


class TextualAgent(Agent):
    def init(self):
        self.setToolsAndExamples('agents/textual')

