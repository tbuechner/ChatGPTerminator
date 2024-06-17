from gpterminator.Agent import Agent


class HighLevelAgent(Agent):

    def __init__(self, gpterminator):
        super().__init__(gpterminator)
        self.setToolsAndExamples('agents/high-level')

