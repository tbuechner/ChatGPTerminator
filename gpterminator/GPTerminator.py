import configparser
import json
import os
import re
import sys
import time
from pathlib import Path


import jsonschema
import climage
import openai
import pyperclip
import requests
import tiktoken
from prompt_toolkit import prompt
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from openai.lib.azure import AzureOpenAI

from jinja2 import Template


class GPTerminator:
    def __init__(self):
        self.config_path = ""
        self.config_selected = ""
        self.model = ""
        self.temperature = ""
        self.presence_penalty = ""
        self.frequency_penalty = ""
        self.msg_hist = []
        self.cmd_init = ""
        self.cmds = {
            "quit": ["q", "quits the program"],
            "help": ["h", "prints a list of acceptable commands"],
            "pconf": [None, "prints out the users current config file"],
            "setconf": [None, "switches to a new config"],
            "regen": ["re", "generates a new response from the last message"],
            "new": ["n", "removes chat history and starts a new session"],
            "load": ["l", "loads a previously saved chatlog"],
            "save": ["s", "saves the chat history"],
            "ifile": [None, "allows the user to analyze files with a prompt"],
            "cpyall": ["ca", "copies all raw text from the previous response"],
            "ccpy": ["cc", "copies code blocks from the last response"],
            "apply": ["a", "applies the function calls"],
            "run": ["r", "run types prompt"]
        }
        self.api_key = ""
        self.prompt_count = 0
        self.save_path = ""
        self.console = Console()


    def getConfigPath(self):
        if "APPDATA" in os.environ:
            confighome = os.environ["APPDATA"]
        elif "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ["XDG_CONFIG_HOME"]
        else:
            confighome = os.path.join(os.environ["HOME"], ".config")
        configpath = os.path.join(confighome, "gpterminator", "config.ini")
        print("configpath: " + configpath)
        self.config_path = configpath

    def loadConfig(self):
        self.getConfigPath()
        config = configparser.ConfigParser()
        config.read(self.config_path)

        self.cmd_init = config["COMMON"]["CommandInitiator"]
        self.save_path = config["COMMON"]["SavePath"]
        self.temperature = config["COMMON"]["Temperature"]
        self.presence_penalty = config["COMMON"]["PresencePenalty"]
        self.frequency_penalty = config["COMMON"]["FrequencyPenalty"]
        self.code_theme = config["COMMON"]["CodeTheme"]

        self.config_selected = config["SELECTED_CONFIG"]["ConfigName"]

        if(self.config_selected == "AZURE_CONFIG"):
            self.model = config[self.config_selected]["Model"]
            self.azure_openai_api_key = config[self.config_selected]["AZURE_OPENAI_API_KEY"]
            self.azure_openai_endpoint = config[self.config_selected]["AZURE_OPENAI_ENDPOINT"]
            self.azure_deployment = config[self.config_selected]["AZURE_DEPLOYMENT"]
            self.api_version = config[self.config_selected]["ApiVersion"]

        if(self.config_selected == "OPENAI_CONFIG"):
            self.openai_key = config[self.config_selected]["API_KEY"]
            self.model = config[self.config_selected]["Model"]


    def init(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.setApiKey()

        if(self.config_selected == "AZURE_CONFIG"):
            self.client = AzureOpenAI(
                api_version = self.api_version,
                azure_endpoint = self.azure_openai_endpoint,
                azure_deployment = self.azure_deployment,
                api_key = self.azure_openai_api_key
            )
        elif(self.config_selected == "OPENAI_CONFIG"):
            self.client = openai
            openai.api_key = self.openai_key

        # self.setToolsAndExamples('functions/fine-granular')

        # self.setToolsAndExamples('functions/high-level')

        # self.setToolsAndExamples('functions/textual')

        self.setToolsAndExamples('functions/textual-diff')
        self.apply_function_handler = textualDiffApplyFunctionHandler

        # self.setToolsAndExamples('functions/one-pass')

        self.generatePrompt()

    def printError(self, msg):
        self.console.print(Panel(f"[bold red]ERROR: [/]{msg}", border_style="red"))

    def printCmds(self):
        self.console.print(f"[bold bright_black]Command : description[/]")
        for cmd, desc in self.cmds.items():
            short = "" if desc[0] is None else f"({desc[0]})"
            self.console.print(f"[bright_black]{self.cmd_init}{cmd} {short}: {desc[1]}[/]")

    def saveChat(self):
        if self.prompt_count == 0:
            self.printError("cant save an empty discussion")
        else:
            self.console.print(
                f"[yellow]|{self.cmd_init}|[/][bold green] Name this chat[/bold green][bold gray] > [/bold gray]",
                end="",
            )
            user_in = prompt().strip().replace(" ", "_")
            with open(Path(self.save_path) / f"{user_in}.json", "w") as f:
                json.dump(self.msg_hist, f, indent=4)
            self.console.print(f"[bright_black]Saved file as {user_in}.json[/]")

    def copyCode(self):
        last_resp = self.msg_hist[-1]["content"]
        code_block_list = []
        index = 1
        while True:
            try:
                code_block = last_resp.split("```")[index]
                lexer = code_block.split("\n")[0]
                code_block = "\n".join(code_block.split("\n")[1:])
                code_block_list.append(code_block)
            except:
                lst_len = len(code_block_list)
                if lst_len == 1:
                    pyperclip.copy(code_block_list[0])
                    self.console.print(f"[bright_black]Copied text to keyboard...[/]")
                elif lst_len > 1:
                    choice_list = []
                    for num, code_block in enumerate(code_block_list):
                        code_block = Syntax(code_block, lexer)
                        choice = Panel(
                            code_block,
                            title=f"[bright_black]Option[/] [red]{num + 1}[/]",
                            border_style="bright_black",
                            style="bold",
                        )
                        choice_list.append(choice)
                    self.console.print(Columns(choice_list))
                    while True:
                        self.console.print(
                            f"[yellow]|{self.cmd_init}|[/][bold green] Which code block do you want [/bold green][bold gray]> [/bold gray]",
                            end="",
                        )
                        try:
                            idx = int(input())
                            if idx >= 1 and idx <= len(code_block_list):
                                break
                        except:
                            pass
                        self.printError("incorrect input, try again")
                    pyperclip.copy(code_block_list[idx - 1])
                    self.console.print(f"[bright_black]Copied text to keyboard...[/]")
                else:
                    self.printError("could not find code in previous response")
                return
            index += 2

    def printConfig(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        self.console.print(f"[bold bright_black]Config Path: {self.config_path}")
        self.console.print("[bold bright_black]Setting: value")
        for setting in config[self.config_selected]:
            self.console.print(
                f"[bright_black]{setting}: {config[self.config_selected][setting]}[/]"
            )

    def loadChatlog(self):
        self.console.print("[bold bright_black]Available saves:[/]")
        file_dict = {}
        for idx, file_name in enumerate(os.listdir(f"{self.save_path}")):
            file_str = file_name.split(".")[0]
            file_dict[idx + 1] = file_str
            self.console.print(f"[bold bright_black]({idx + 1}) > [/][red]{file_str}[/]")
        if len(file_dict) == 0:
            self.printError("you have no saved chats")
            return
        while True:
            self.console.print(
                f"[yellow]|{self.cmd_init}|[/][bold green] Select a file to load [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            selection = input()
            if selection.isdigit() == True and int(selection) in file_dict:
                break
            else:
                self.printError(f"{selection} is not a valid selection")
        with open(Path(f"{self.save_path}") / f"{file_dict[int(selection)]}.json", "r") as f:
            save = json.load(f)
        self.prompt_count = 0
        self.msg_hist = save
        for msg in save:
            role = msg["role"]
            if role == "user":
                self.console.print(
                    f"[yellow]|{self.prompt_count}|[/][bold green] Input [/bold green][bold gray]> [/bold gray]",
                    end="",
                )
                self.console.print(msg["content"])
                self.prompt_count += 1
            elif role == "assistant":
                encoding = tiktoken.encoding_for_model(self.model)
                num_tokens = len(encoding.encode(msg["content"]))
                subtitle_str = f"[bright_black]Tokens:[/] [bold red]{num_tokens}[/]"
                md = Panel(
                    Markdown(msg["content"], self.code_theme),
                    border_style="bright_black",
                    title="[bright_black]Assistant[/]",
                    title_align="left",
                    subtitle=subtitle_str,
                    subtitle_align="right",
                )
                self.console.print(md)
                self.console.print()
            else:
                pass

    def copyAll(self):
        if self.prompt_count == 0:
            self.printError("cannot run cpyall when there are no responses")
            return
        last_resp = self.msg_hist[-1]["content"]
        pyperclip.copy(last_resp)
        self.console.print(f"[bright_black]Copied text to keyboard...[/]")

    def analyzeFile(self):
        while True:
            self.console.print(
                f"[yellow]|!|[/][bold green] Provide the file path to analyze [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            user_in = prompt().strip()
            if os.path.exists(user_in):
                with open(user_in, "r") as file:
                    file_content = file.read()
                break
            else:
                self.printError(f"{user_in} cannot be found")

        while True:
            self.console.print(
                f"[yellow]|{self.prompt_count}|[/][bold green] Prompt for {user_in} [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            user_prmt = prompt().strip()
            if user_prmt != "":
                break
            else:
                self.printError(f"you cannot have an empty prompt")

        msg = f"{user_prmt}: '{file_content}'"
        self.prompt_count += 1
        self.getResponse(msg)

    def queryUser(self):
        self.console.print(
            f"[yellow]|{self.prompt_count}|[/][bold green] Input [/bold green][bold gray]> [/bold gray]",
            end="",
        )
        user_in = prompt().strip()
        if user_in == "":
            self.printError("user input is empty")
        elif user_in[0] == self.cmd_init:
            raw_cmd = user_in.split(self.cmd_init)
            cmd = raw_cmd[1].lower().split()[0]
            if cmd in self.cmds or cmd in [shrt[0] for shrt in self.cmds.values()]:
                if cmd == "quit" or cmd == "q":
                    sys.exit()
                elif cmd == "help" or cmd == "h":
                    self.printCmds()
                elif cmd == "regen" or cmd == "re":
                    if self.prompt_count > 0:
                        self.msg_hist.pop(-1)
                        last_msg = self.msg_hist.pop(-1)["content"]
                        self.prompt_count -= 1
                        return last_msg
                    else:
                        self.printError("can't regenenerate, there is no previous prompt")
                elif cmd == "save" or cmd == "s":
                    self.saveChat()
                elif cmd == "ccpy" or cmd == "cc":
                    if self.prompt_count > 0:
                        self.copyCode()
                    else:
                        self.printError("can't copy, there is no previous response")
                elif cmd == "pconf":
                    self.printConfig()
                elif cmd == "load" or cmd == "l":
                    self.loadChatlog()
                elif cmd == "cpyall" or cmd == "ca":
                    self.copyAll()
                elif cmd == "ifile":
                    self.analyzeFile()
                elif cmd == "new" or cmd == "n":
                    self.msg_hist = self.msg_hist[:1]
                    self.prompt_count = 0
                    self.printBanner()
                elif cmd == "apply" or cmd == "a":
                    self.applyFunctionCalls()
                elif cmd == "run" or cmd == "r":
                    self.runTypesPrompt()
            else:
                self.printError(
                    f"{self.cmd_init}{cmd} in not in the list of commands, type {self.cmd_init}help"
                )
        else:
            return user_in

    def getResponse(self, usr_prompt):
        self.msg_hist.append({"role": "user", "content": usr_prompt})
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=self.msg_hist,
                stream=True,
                temperature=float(self.temperature),
                presence_penalty=float(self.presence_penalty),
                frequency_penalty=float(self.frequency_penalty),
                tools=self.tools
            )
        except openai.APITimeoutError as e:
            self.printError(f"OpenAI API request timed out: {e}")
            sys.exit()
        except openai.APIError as e:
            self.printError(f"OpenAI API returned an API Error: {e}")
            sys.exit()
        except openai.APIConnectionError as e:
            self.printError(f"OpenAI API request failed to connect: {e}")
            sys.exit()
        except openai.BadRequestError as e:
            self.printError(f"OpenAI API request was invalid: {e}")
            sys.exit()
        except openai.AuthenticationError as e:
            self.printError(f"OpenAI API request was not authorized: {e}")
            sys.exit()
        except openai.PermissionDeniedError as e:
            self.printError(f"OpenAI API request was not permitted: {e}")
            sys.exit()
        except openai.RateLimitError as e:
            self.printError(f"OpenAI API request exceeded rate limit: {e}")
            sys.exit()

        subtitle_str = f"[bright_black]Tokens:[/] [bold red]{0}[/] | "
        subtitle_str += f"[bright_black]Time Elapsed:[/][bold yellow] {0.0}s [/]"
        md = Panel(
            Markdown("", self.code_theme),
            border_style="bright_black",
            title="[bright_black]Assistant[/]",
            title_align="left",
            subtitle=subtitle_str,
            subtitle_align="right",
        )

        start_time = time.time()

        function_name_2_arguments = {}
        # full_reply_content = ""
        full_reply_content_shortened = ""
        function_name = None
        function_arguments = ""
        log = ""

        with Live(md, console=self.console, transient=True) as live:
            for chunk in resp:
                for choice in chunk.choices:
                    chunk_message = choice.delta  # extract the message

                    if(chunk_message.tool_calls):
                        for tool_call in chunk_message.tool_calls:
                            log += f"tool_call\n"
                            function_call_arguments = tool_call.function.arguments
                            function_arguments += function_call_arguments
                            log += f"function_call_arguments: {function_call_arguments}\n"
                            if tool_call.function.name is not None:
                                log += f"tool_call.function.name: {tool_call.function.name}\n"
                                if function_name is not None:
                                    # full_reply_content += "\n```\n"
                                    self.addToFunctionName2Arguments(function_name, function_arguments, function_name_2_arguments)

                                function_name = tool_call.function.name

                                # full_reply_content += "Function: " + function_name + "\n"
                                full_reply_content_shortened += "Function: " + function_name + "\n"
                                # full_reply_content += "```json\n"
                                function_arguments = ""

                            # full_reply_content += "".join(function_call_arguments)

                    if chunk_message.content is not None:
                        # full_reply_content += "".join(chunk_message.content)
                        full_reply_content_shortened += "".join(chunk_message.content)

                    encoding = tiktoken.encoding_for_model(self.model)
                    num_tokens = len(encoding.encode(full_reply_content_shortened))
                    time_elapsed_s = time.time() - start_time
                    subtitle_str = f"[bright_black]Tokens:[/] [bold red]{num_tokens}[/] | "
                    subtitle_str += (
                        f"[bright_black]Time Elapsed:[/][bold yellow] {time_elapsed_s:.1f}s [/]"
                    )
                    md = Panel(
                        Markdown(full_reply_content_shortened, self.code_theme),
                        border_style="bright_black",
                        title="[bright_black]Assistant[/]",
                        title_align="left",
                        subtitle=subtitle_str,
                        subtitle_align="right",
                    )
                    live.update(md)

        if function_name is not None:
            self.addToFunctionName2Arguments(function_name, function_arguments, function_name_2_arguments)

        # print("function_name_2_arguments: " + str(function_name_2_arguments))

        # print(str(function_name_2_arguments))
        file_names = self.saveFunctionCalls(function_name_2_arguments, full_reply_content_shortened)
        self.function_name_2_arguments = function_name_2_arguments

        # if function_name_2_arguments:
        #     for function_name, arguments in function_name_2_arguments.items():
        #         print(f"Function name: {function_name}")
        #         print(f"Argument: {arguments}\n")

        self.console.print(md)
        self.console.print()
        self.msg_hist.append({"role": "assistant", "content": full_reply_content_shortened})

    def addToFunctionName2Arguments(self, function_name, function_arguments, function_name_2_arguments):
        if function_name in function_name_2_arguments:
            function_name_2_arguments[function_name].append(function_arguments)
        else:
            function_name_2_arguments[function_name] = [function_arguments]

    def applyFunctionCalls(self):
        # print("applyFunctionCalls, self.function_name_2_arguments: " + str(self.function_name_2_arguments))
        if self.function_name_2_arguments and self.apply_function_handler is not None:
            # iterate over the function_name_2_arguments dictionary
            for function_name, arguments in self.function_name_2_arguments.items():
                # print(f"Function name: {function_name}")
                # print(f"Argument: {arguments}\n")
                self.apply_function_handler(self, function_name, arguments)

    def runTypesPrompt(self):
        with open('data-model-narrative/okr-2/generated/prompt.md', 'r') as file:
            prompt = file.read()

        self.getResponse(prompt)

    def saveFunctionCalls(self, function_name_2_arguments, full_reply_content):
        file_names = []
        if full_reply_content:
            file_name = f"{self.get_file_name()}.md"
            file_names.append(file_name)
            with open(Path(self.save_path) / file_name, "w") as f:
                f.write(full_reply_content)

        if function_name_2_arguments:
            for function_name, arguments in function_name_2_arguments.items():
                if function_name is not None and arguments is not None:
                    for argument in arguments:
                        file_name = f"{self.get_file_name()}-{function_name}.json"
                        file_names.append(file_name)
                        with open(Path(self.save_path) / file_name, "w") as f:
                            json_object = json.loads(argument)
                            json.dump(json_object, f, indent=4)

                    # validate arguments against the schema
                    # q: how to validate a json against a schema in python programatically

                    # schema = json.loads(self.json_schema)
                    # try:
                    #     jsonschema.validate(instance=json_object, schema=schema)
                    #     print("JSON object is valid")
                    # except jsonschema.exceptions.ValidationError as ve:
                    #     print("JSON object is not valid.")

        return file_names

    def get_file_name(self):
        pattern = r'^\d{4}-'
        max_file_number = 0
        for idx, file_name in enumerate(os.listdir(f"{self.save_path}")):
            # test if file_name starts with four digits followed by "-", e.g., 0003-
            if re.match(pattern, file_name):
                file_str = file_name.split("-")[0]
                if idx == 0:
                    max_file_number = file_str
                else:
                    if file_str > max_file_number:
                        max_file_number = file_str
        # increment the number by 1
        new_file_number = int(max_file_number) + 1
        file_name = f"{new_file_number:04d}"
        return file_name


    def setApiKey(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key == None or self.api_key == "":
            self.printError("the OPENAI_API_KEY environment variable is missing")
            sys.exit()

    def printBanner(self):
        welcome_ascii = """                                                        
 _____ _____ _____               _         _           
|   __|  _  |_   _|___ ___ _____|_|___ ___| |_ ___ ___ 
|  |  |   __| | | | -_|  _|     | |   | .'|  _| . |  _|
|_____|__|    |_| |___|_| |_|_|_|_|_|_|__,|_| |___|_|  
"""
        self.console.print(f"[bold green]{welcome_ascii}[/bold green]", end="")
        self.console.print(f"[bright_black]Version: v0.1.11[/]")
        self.console.print(f"[bright_black]Model: {self.model}[/]")
        self.console.print(
            f"[bright_black]Type '{self.cmd_init}quit' to quit the program; '{self.cmd_init}help' for a list of cmds[/]\n"
        )

    def checkDirs(self):
        # get paths
        if "APPDATA" in os.environ:
            confighome = os.environ["APPDATA"]
        elif "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ["XDG_CONFIG_HOME"]
        else:
            confighome = os.path.join(os.environ["HOME"], ".config")
        configpath = os.path.join(confighome, "gpterminator")
        savespath = os.path.join(configpath, "saves")

        # check if paths/files exist
        config_exists = os.path.exists(os.path.join(configpath, "config.ini"))
        configpath_exists = os.path.exists(configpath)
        saves_exist = os.path.exists(savespath)

        if configpath_exists == False:
            self.console.print(f"[bright_black]Initializing config path ({configpath})...[/]")
            os.mkdir(configpath)

        # make paths/files
        if config_exists == False:
            full_config_path = os.path.join(configpath, "config.ini")
            self.console.print(f"[bright_black]Initializing config file ({full_config_path})...[/]")
            config = configparser.ConfigParser()
            config["SELECTED_CONFIG"] = {"configname": "BASE_CONFIG"}
            config["BASE_CONFIG"] = {
                "ModelName": "gpt-3.5-turbo",
                "Temperature": "1",
                "PresencePenalty": "0",
                "FrequencyPenalty": "0",
                "SystemMessage": "You are a helpful assistant named GPTerminator.",
                "CommandInitiator": "!",
                "SavePath": f"{savespath}",
                "CodeTheme": "monokai",
            }
            with open(full_config_path, "w") as configfile:
                config.write(configfile)

        if saves_exist == False:
            self.console.print(f"[bright_black]Initializing save path ({savespath})...[/]")
            os.mkdir(savespath)

    def run(self, passed_input=None):
        self.checkDirs()
        self.loadConfig()
        self.init()
        self.printBanner()

        if passed_input is not None:
            self.prompt_count += 1
            self.getResponse(passed_input)

        while True:
            usr_input = self.queryUser()

            if usr_input is not None:
                self.prompt_count += 1
                self.getResponse(usr_input)


    def generatePrompt(self):
        folder_name_generated = 'data-model-narrative/okr-2/generated'
        if os.path.exists(folder_name_generated):
            os.system("rm -r " + folder_name_generated)

        # create folder folder_name_generated
        os.mkdir(folder_name_generated)

        # load content of file types.json into the variable types
        with open('data-model-narrative/okr-2/types.json', 'r') as file:
            types = json.load(file)

        rendered = self.renderTemplate("data-model-narrative/okr-2/types-template.md", types)
        with open(os.path.join(folder_name_generated, "types.md"), "w") as new_file:
            new_file.write(rendered)

        rendered = self.renderTemplate("data-model-narrative/okr-2/prompt.md")
        with open(os.path.join(folder_name_generated, "prompt.md"), "w") as new_file:
            new_file.write(rendered)


    def setToolsAndExamples(self, folder_name):
        with open(os.path.join(folder_name, "system_prompt.txt"), "r") as file:
            self.msg_hist.append({"role": "system", "content": file.read()})

        tools = []
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                # if the file is a .txt file
                if file.endswith('function.json'):
                    # render the template
                    template_file = os.path.join(root, file)
                    rendered_string = self.renderTemplate(template_file)

                    # parse the rendered string to a dictionary
                    tool = json.loads(rendered_string)
                    # print("adding tool: " + file)
                    tools.append(tool)
                if file.endswith('generate_boolean_attribute_example_msg.json'):
                    # render the template
                    template_file = os.path.join(root, file)
                    rendered_string = self.renderTemplate(template_file)

                    # parse the rendered string to a dictionary
                    example = json.loads(rendered_string)
                    # print("adding example: " + file)
                    self.msg_hist.append(example)
        if tools:
            self.tools = tools
        else:
            self.tools = None

    def renderTemplate(self, template_file, data=None):
        # Read the template file
        with open(template_file, "r") as file:
            template_string = file.read()

        # Create a template object
        template = Template(template_string)

        # Render the template with the file contents
        rendered_string = template.render(
            load_file=loadFile,
            data=data
        )

        return rendered_string

def loadFile(file_path):
    # Read the contents of the file
    with open(file_path, "r") as file:
        return file.read()

def textualDiffApplyFunctionHandler(self, function_name, arguments):
    with open('data-model-narrative/okr-2/types.json', 'r') as file:
        types = json.load(file)

    if 'add_type' == function_name:
        for argument in arguments:
            argument_dict = json.loads(argument)
            types.append(argument_dict)

    if 'add_attribute' == function_name:
        for argument in arguments:
            argument_dict = json.loads(argument)
            for type_ in types:
                if type_['name'] == argument_dict['typeName']:
                    type_attributes = type_['attributes']
                    type_attributes.append(argument_dict)

    if 'delete_attribute' == function_name:
        for argument in arguments:
            argument_dict = json.loads(argument)
            for type_ in types:
                if type_['name'] == argument_dict['typeName']:
                    type_attributes = type_['attributes']
                    for i, attribute in enumerate(type_attributes):
                        if attribute['name'] == argument_dict['name']:
                            type_attributes.pop(i)

    if 'delete_type' == function_name:
        for argument in arguments:
            argument_dict = json.loads(argument)
            for i, type in enumerate(types):
                if type['name'] == argument_dict['name']:
                    types.pop(i)

    # write the types to the types.json file
    with open('data-model-narrative/okr-2/types.json', 'w') as file:
        json.dump(types, file, indent=4)

    self.generatePrompt()

    self.msg_hist = self.msg_hist[:1]
    self.prompt_count = 0
    self.printBanner()

