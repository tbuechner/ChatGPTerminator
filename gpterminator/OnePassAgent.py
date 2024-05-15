from gpterminator.Agent import Agent


class OnePassAgent(Agent):
    def init(self):
        self.setToolsAndExamples('agents/one-pass')

