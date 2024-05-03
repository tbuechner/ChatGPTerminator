import configparser
import json
import os
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



class GPTerminator:
    def __init__(self):
        self.config_path = ""
        self.config_selected = ""
        self.model = ""
        self.temperature = ""
        self.presence_penalty = ""
        self.frequency_penalty = ""
        self.sys_prmpt = ""
        self.msg_hist = []
        self.cmd_init = ""
        self.cmds = {
            "quit": ["q", "quits the program"],
            "help": ["h", "prints a list of acceptable commands"],
            "pconf": [None, "prints out the users current config file"],
            "setconf": [None, "switches to a new config"],
            "regen": ["r", "generates a new response from the last message"],
            "new": ["n", "removes chat history and starts a new session"],
            "load": ["l", "loads a previously saved chatlog"],
            "save": ["s", "saves the chat history"],
            "ifile": [None, "allows the user to analyze files with a prompt"],
            "cpyall": ["ca", "copies all raw text from the previous response"],
            "ccpy": ["cc", "copies code blocks from the last response"]
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

        self.sys_prmpt = config["COMMON"]["SystemMessage"]
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
        self.msg_hist.append({"role": "system", "content": self.sys_prmpt})

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

        # with open("system_prompt.txt", "r") as file:
        #     self.system_prompt = file.read()
        #
        # with open("json-schema.json", "r") as file:
        #     self.generate_data_model_schema = json.loads(file.read())

        with open("../json-schemas/just-types/type-schema.json", "r") as file:
            self.add_type_schema = json.loads(file.read())

        with open("../json-schemas/just-types/type-example-1.json", "r") as file:
            self.add_type_example_1 = file.read()

        with open("../json-schemas/attributes/boolean-schema.json", "r") as file:
            self.add_boolean_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/date-schema.json", "r") as file:
            self.add_date_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/long-text-schema.json", "r") as file:
            self.add_long_text_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/number-enumeration-schema.json", "r") as file:
            self.add_number_enumeration_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/number-schema.json", "r") as file:
            self.add_number_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/reference-schema.json", "r") as file:
            self.add_reference_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/rich-string-schema.json", "r") as file:
            self.add_rich_string_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/string-enumeration-schema.json", "r") as file:
            self.add_string_enumeration_attribute_schema = json.loads(file.read())
        with open("../json-schemas/attributes/string-schema.json", "r") as file:
            self.add_string_attribute_schema = json.loads(file.read())

        with open("../json-schemas/attributes/boolean-example-1.json", "r") as file:
            self.add_boolean_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/date-example-1.json", "r") as file:
            self.add_date_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/long-text-example-1.json", "r") as file:
            self.add_long_text_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/number-enumeration-example-1.json", "r") as file:
            self.add_number_enumeration_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/number-example-1.json", "r") as file:
            self.add_number_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/reference-example-1.json", "r") as file:
            self.add_reference_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/rich-string-example-1.json", "r") as file:
            self.add_rich_string_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/string-enumeration-example-1.json", "r") as file:
            self.add_string_enumeration_attribute_example_1 = file.read()
        with open("../json-schemas/attributes/string-example-1.json", "r") as file:
            self.add_string_attribute_example_1 = file.read()

        self.msg_hist.append({
            "role": "function",
            "name": "generate_type",
            "content": self.add_type_example_1})

        self.msg_hist.append({
            "role": "function",
            "name": "generate_boolean_attribute",
            "content": self.add_boolean_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_date_attribute",
            "content": self.add_date_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_long_text_attribute",
            "content": self.add_long_text_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_number_enumeration_attribute",
            "content": self.add_number_enumeration_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_number_attribute",
            "content": self.add_number_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_reference_attribute",
            "content": self.add_reference_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_rich_string_attribute",
            "content": self.add_rich_string_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_string_enumeration_attribute",
            "content": self.add_string_enumeration_attribute_example_1})
        self.msg_hist.append({
            "role": "function",
            "name": "generate_string_attribute",
            "content": self.add_string_attribute_example_1})


        self.tools = [
            # {
            #     "type": "function",
            #     "function": {
            #         'name': 'generate_data_model',
            #         'description': 'Generate a data model from the body of the input text',
            #         'parameters': self.generate_data_model_schema
            #     }
            # },
            {
                "type": "function",
                "function": {
                    'name': 'generate_type',
                    'description': 'Generate a type and add it to the data model. This is similar to adding a new table to a SQL database.',
                    'parameters': self.add_type_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_boolean_attribute',
                    'description': 'Generate a new boolean attribute and add it to a type. Values of boolean attributes are either true or false.',
                    'parameters': self.add_boolean_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_date_attribute',
                    'description': 'Generate a new date attribute and add it to a type.',
                    'parameters': self.add_date_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_long_text_attribute',
                    'description': 'Generate a new long text attributeand add it to a type. Long text attributes are used for large amounts of text.',
                    'parameters': self.add_long_text_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_number_enumeration_attribute',
                    'description': 'Generate a new number enumeration attribute and add it to a type. Number enumeration attributes are used if there is a given set of allowed numbers.',
                    'parameters': self.add_number_enumeration_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_number_attribute',
                    'description': 'Generate a new number attribute and add it to a type. Number attributes are used for numerical values.',
                    'parameters': self.add_number_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_reference_attribute',
                    'description': 'Generate a new reference attribute and add it to a type. Reference attributes are used to reference another type. Similar to a foreign key in a SQL database.',
                    'parameters': self.add_reference_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_rich_string_attribute',
                    'description': 'Generate a new rich string attribute and add it to a type. A rich string attribute is a string that can contain rich text such as bold, italic, and underline, tables, images, ...',
                    'parameters': self.add_rich_string_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_string_enumeration_attribute',
                    'description': 'Generate a new text enumeration attribute and add it to a type. String enumeration attributes are used if there is a given set of allowed strings.',
                    'parameters': self.add_string_enumeration_attribute_schema
                }
            },
            {
                "type": "function",
                "function": {
                    'name': 'generate_string_attribute',
                    'description': 'Generate a new string attribute and add it to a type.',
                    'parameters': self.add_string_attribute_schema
                }
            }
        ]


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
                elif cmd == "regen" or cmd == "r":
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
            else:
                self.printError(
                    f"{self.cmd_init}{cmd} in not in the list of commands, type {self.cmd_init}help"
                )
        else:
            return user_in

    def getResponse(self, usr_prompt):
        self.msg_hist.append({"role": "user", "content": usr_prompt})
        try:
            # resp = openai.ChatCompletion.create(
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
        except openai.InvalidRequestError as e:
            self.printError(f"OpenAI API request was invalid: {e}")
            sys.exit()
        except openai.AuthenticationError as e:
            self.printError(f"OpenAI API request was not authorized: {e}")
            sys.exit()
        except openai.PermissionError as e:
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
        full_reply_content = ""
        function_name = None

        with Live(md, console=self.console, transient=True) as live:
            for chunk in resp:
                for choice in chunk.choices:
                    chunk_message = choice.delta  # extract the message

                    if(chunk_message.tool_calls):
                        for tool_call in chunk_message.tool_calls:
                            function_call_arguments = tool_call.function.arguments
                            if tool_call.function.name is not None:
                                if function_name is not None:
                                    full_reply_content += "\n```\n"

                                function_name = tool_call.function.name
                                full_reply_content += "Function: " + function_name + "\n"
                                full_reply_content += "```json\n"
                            if function_name in function_name_2_arguments:
                                function_name_2_arguments[function_name] = function_name_2_arguments[function_name] + function_call_arguments
                            else:
                                function_name_2_arguments[function_name] = function_call_arguments
                            full_reply_content += "".join(function_call_arguments)
                            # full_reply_content += "```\n"

                    if chunk_message.content is not None:
                        full_reply_content += "".join(chunk_message.content)

                    encoding = tiktoken.encoding_for_model(self.model)
                    num_tokens = len(encoding.encode(full_reply_content))
                    time_elapsed_s = time.time() - start_time
                    subtitle_str = f"[bright_black]Tokens:[/] [bold red]{num_tokens}[/] | "
                    subtitle_str += (
                        f"[bright_black]Time Elapsed:[/][bold yellow] {time_elapsed_s:.1f}s [/]"
                    )
                    md = Panel(
                        Markdown(full_reply_content, self.code_theme),
                        border_style="bright_black",
                        title="[bright_black]Assistant[/]",
                        title_align="left",
                        subtitle=subtitle_str,
                        subtitle_align="right",
                    )
                    live.update(md)

        # self.saveDataModel(function_name_2_arguments)

        # if function_name_2_arguments:
        #     for function_name, arguments in function_name_2_arguments.items():
        #         print(f"Function name: {function_name}")
        #         print(f"Argument: {arguments}\n")

        self.console.print(md)
        self.console.print()
        self.msg_hist.append({"role": "assistant", "content": full_reply_content})


    def saveDataModel(self, function_name_2_arguments):
        if function_name_2_arguments:
            for function_name, arguments in function_name_2_arguments.items():
                if function_name is not None and arguments is not None:
                    if function_name == "generate_data_model":
                        # find all files with name "data_model_xxxx.json" - xxxx is a number starting with 0000 - find the highest number
                        max_file_number = 0
                        for idx, file_name in enumerate(os.listdir(f"{self.save_path}")):
                            if file_name.startswith("data_model_"):
                                file_str = file_name.split(".")[0]
                                file_number = file_str.split("_")[2]
                                if idx == 0:
                                    max_file_number = file_number
                                else:
                                    if file_number > max_file_number:
                                        max_file_number = file_number
                        # increment the number by 1
                        new_file_number = int(max_file_number) + 1
                        # write to a file with the name "data_model_xxxx.json"
                        file_name = f"data_model_{new_file_number:04d}"
                        json_object = json.loads(arguments)
                        with open(Path(self.save_path) / f"{file_name}.json", "w") as f:
                            # parse the arguments to json
                            json.dump(json_object, f, indent=4)

                        # validate arguments against the schema
                        # q: how to validate a json against a schema in python programatically

                        # schema = json.loads(self.json_schema)
                        # try:
                        #     jsonschema.validate(instance=json_object, schema=schema)
                        #     print("JSON object is valid")
                        # except jsonschema.exceptions.ValidationError as ve:
                        #     print("JSON object is not valid.")


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
        self.console.print(f"[bright_black]System prompt: {self.sys_prmpt}[/]")
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
