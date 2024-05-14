from gpterminator.Agent import Agent


class OnePassAgent(Agent):
    def init(self):
        self.setToolsAndExamples('functions/one-pass')

