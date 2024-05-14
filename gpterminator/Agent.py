import json
import os

from gpterminator.Utils import renderTemplate


class Agent:
    def __init__(self, gpterminator):
        self.gpterminator = gpterminator

    def init(self):
        # self.setToolsAndExamples('functions/fine-granular')

        # self.setToolsAndExamples('functions/high-level')

        # self.setToolsAndExamples('functions/textual')

        # self.application_name = 'okr-2'
        self.application_name = 'large-safe'
        # self.application_name = 'resource-management'

        self.setToolsAndExamples('functions/textual-diff')
        self.apply_function_handler = textualDiffApplyFunctionHandler

        # self.setToolsAndExamples('functions/one-pass')
        self.generateAllPrompts()


    def applyFunctionCalls(self):
        # print("applyFunctionCalls, self.function_name_2_arguments: " + str(self.function_name_2_arguments))
        if self.gpterminator.function_name_2_arguments and self.apply_function_handler is not None:
            # iterate over the function_name_2_arguments dictionary
            for function_name, arguments in self.gpterminator.function_name_2_arguments.items():
                # print(f"Function name: {function_name}")
                # print(f"Argument: {arguments}\n")
                self.apply_function_handler(self, function_name, arguments)

    def runTypesPrompt(self):
        with open('data-model-narrative/' + self.application_name + '/generated/prompt.md', 'r') as file:
            prompt = file.read()

        # print("prompt: " + prompt)

        self.gpterminator.getResponse(prompt)


    def generateAllPrompts(self):
        for dir in os.listdir('data-model-narrative'):
            if os.path.isdir(os.path.join('data-model-narrative', dir)):
                folder_name_generated = 'data-model-narrative/' + dir + '/generated'
                if os.path.exists(folder_name_generated):
                    os.system("rm -r " + folder_name_generated)

                # create folder folder_name_generated
                os.mkdir(folder_name_generated)

                # load content of file types.json into the variable types
                with open('data-model-narrative/' + dir + '/types.json', 'r') as file:
                    types = json.load(file)

                rendered = renderTemplate('data-model-narrative/types-template.md', types)
                with open(os.path.join(folder_name_generated, "types.md"), "w") as new_file:
                    new_file.write(rendered)

                rendered = renderTemplate('data-model-narrative/prompt-template.md', None, dir)
                with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
                    new_file.write(rendered)


    def setToolsAndExamples(self, folder_name):
        with open(os.path.join(folder_name, "system_prompt.txt"), "r") as file:
            system_prompt = file.read()
            # print("system_prompt: " + system_prompt)
            self.gpterminator.msg_hist.append({"role": "system", "content": system_prompt})

        tools = []
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                # if the file is a .txt file
                if file.endswith('function.json'):
                    # render the template
                    template_file = os.path.join(root, file)
                    rendered_string = renderTemplate(template_file)

                    # parse the rendered string to a dictionary
                    tool = json.loads(rendered_string)
                    # print("adding tool: " + file)
                    tools.append(tool)
                if file.endswith('example_msg.json'):
                    # render the template
                    template_file = os.path.join(root, file)
                    rendered_string = renderTemplate(template_file)

                    # parse the rendered string to a dictionary
                    example = json.loads(rendered_string)
                    # print("adding example: " + file)
                    self.gpterminator.msg_hist.append(example)

        if tools:
            self.gpterminator.tools = tools
        else:
            self.gpterminator.tools = None

    def handleFunction(self, function_name, argument_dict, types):
        if 'add_type' == function_name:
            for type_ in types:
                if type_['name'] == argument_dict['name']:
                    print(f"Type with name {argument_dict['name']} already exists")
                    return
            print(f"Adding type with name {argument_dict['name']}")
            types.append(argument_dict)
            return

        if 'add_attribute' == function_name:
            for type_ in types:
                if type_['name'] == argument_dict['typeName']:
                    type_attributes = type_['attributes']
                    type_attributes.append(argument_dict['attribute'])
                    print(f"Adding attribute with name {argument_dict['attribute']['name']} to type {argument_dict['typeName']}")
                    return
            print(f"Type with name {argument_dict['typeName']} does not exist")
            return

        if 'delete_attribute' == function_name:
            for type_ in types:
                if type_['name'] == argument_dict['typeName']:
                    type_attributes = type_['attributes']
                    for i, attribute in enumerate(type_attributes):
                        if attribute['name'] == argument_dict['attributeName']:
                            print(f"Deleting attribute with name {argument_dict['attributeName']} from type {argument_dict['typeName']}")
                            type_attributes.pop(i)
                            return
            print(f"Attribute with name {argument_dict['attributeName']} does not exist in type {argument_dict['typeName']}")

        if 'delete_type' == function_name:
            for i, type in enumerate(types):
                if type['name'] == argument_dict['name']:
                    types.pop(i)
                    print(f"Deleting type with name {argument_dict['name']}")
                    return
            print(f"Type with name {argument_dict['name']} does not exist")
            return

        print(f"Function {function_name} not found")

def textualDiffApplyFunctionHandler(self, function_name, arguments):
    with open('data-model-narrative/' + self.application_name + '/types.json', 'r') as file:
        types = json.load(file)

    print("Applying function calls")
    for argument in arguments:
        argument_dict = json.loads(argument)
        print(f"Function: {function_name}")
        self.handleFunction(function_name, argument_dict, types)

    # write the types to the types.json file
    with open('data-model-narrative/' + self.application_name + '/types.json', 'w') as file:
        json.dump(types, file, indent=4)

    self.generateAllPrompts()

    self.gpterminator.msg_hist = self.gpterminator.msg_hist[:1]
    self.gpterminator.prompt_count = 0

    print("Session has been reset. You can now run the prompt again.")
