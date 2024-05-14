from gpterminator.Agent import Agent


class HighLevelAgent(Agent):
    def init(self):
        self.setToolsAndExamples('functions/high-level')

