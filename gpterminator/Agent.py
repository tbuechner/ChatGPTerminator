import json
import os
import jsonschema

from gpterminator.Utils import renderTemplate


class Agent:
    def __init__(self, gpterminator):
        self.gpterminator = gpterminator


    def runPrompt(self):
        pass


    def applyFunctionCalls(self):
        # print("applyFunctionCalls, self.function_name_2_arguments: " + str(self.function_name_2_arguments))
        if self.gpterminator.function_name_2_arguments and self.apply_function_handler is not None:
            # iterate over the function_name_2_arguments dictionary
            for function_name, arguments in self.gpterminator.function_name_2_arguments.items():
                # print(f"Function name: {function_name}")
                # print(f"Argument: {arguments}\n")
                self.apply_function_handler(self, function_name, arguments)
        else:
            print("No function calls to apply")


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

    def validateSchema(self, argument_dict, function_name):
        for tool in self.gpterminator.tools:
            if tool['function']['name'] == function_name:
                print(f"Tool with name {function_name} found")
                schema = tool['function']['parameters']
                try:
                    jsonschema.validate(instance=argument_dict, schema=schema)
                    print("JSON object is valid")
                    return True
                except jsonschema.exceptions.ValidationError as ve:
                    print("JSON object is not valid:")
                    print(argument_dict)

                    print("Validation error message:", ve.message)
                    print("Path to error:", list(ve.path))
                    print("Schema path:", list(ve.schema_path))
                    print("Schema:", ve.schema)

                    return False

        print(f"Tool with name {function_name} not found")
        return False

    def generateFolderIfNotExists(self, folder_name_generated):
        if os.path.exists(folder_name_generated):
            os.system("rm -r " + folder_name_generated)

        # create folder folder_name_generated
        os.mkdir(folder_name_generated)
