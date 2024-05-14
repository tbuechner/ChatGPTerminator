from gpterminator.Agent import Agent


class FineGranularAgent(Agent):
    def init(self):
        self.setToolsAndExamples('functions/fine-granular')

