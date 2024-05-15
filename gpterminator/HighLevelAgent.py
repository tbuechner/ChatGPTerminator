from gpterminator.Agent import Agent


class HighLevelAgent(Agent):
    def init(self):
        self.setToolsAndExamples('agents/high-level')

