import configparser
import json
import os
import sys
import time
from pathlib import Path


import openai
import pyperclip
import tiktoken
from prompt_toolkit import prompt
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from openai.lib.azure import AzureOpenAI

from gpterminator.FineGranularAttributesAgent import FineGranularAttributesAgent
from gpterminator.FineGranularTypesAgent import FineGranularTypesAgent
from gpterminator.HighLevelAgent import HighLevelAgent
from gpterminator.Utils import get_file_name, addToFunctionName2Arguments

class GPTerminator:
    def __init__(self):
        self.config_path = ""
        self.config_selected = ""
        self.model = ""
        self.temperature = ""
        self.presence_penalty = ""
        self.frequency_penalty = ""
        self.msg_hist = []
        self.cmds = {
            "quit": ["q", "quits the program"],
            "help": ["h", "prints a list of acceptable commands"],
            "regen": ["re", "generates a new response from the last message"],
            "new": ["n", "removes chat history and starts a new session"],
            "copy": ["c", "copies all raw text from the previous response"],
            "run": ["r", "run the types prompt of the agent"],
            "setAgent": ["agent"],
            "setApplication": ["app"]
        }
        self.api_key = ""
        self.prompt_count = 0
        self.save_path = ""
        self.console = Console()


    def loadConfig(self):
        if "APPDATA" in os.environ:
            confighome = os.environ["APPDATA"]
        elif "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ["XDG_CONFIG_HOME"]
        else:
            confighome = os.path.join(os.environ["HOME"], ".config")
        configpath = os.path.join(confighome, "gpterminator", "config.ini")
        print("configpath: " + configpath)
        self.config_path = configpath
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.save_path = self.config["COMMON"]["SavePath"]
        self.temperature = self.config["COMMON"]["Temperature"]
        self.presence_penalty = self.config["COMMON"]["PresencePenalty"]
        self.frequency_penalty = self.config["COMMON"]["FrequencyPenalty"]
        self.code_theme = self.config["COMMON"]["CodeTheme"]

        self.config_selected = self.config["SELECTED_CONFIG"]["ConfigName"]
        self.model = self.config[self.config_selected]["Model"]


    def printError(self, msg):
        self.console.print(Panel(f"[bold red]ERROR: [/]{msg}", border_style="red"))

    def printCmds(self):
        self.console.print(f"[bold bright_black]Command : description[/]")
        for cmd, desc in self.cmds.items():
            short = "" if desc[0] is None else f"({desc[0]})"
            self.console.print(f"[bright_black]!{cmd} {short}: {desc[1]}[/]")


    def copyAll(self):
        if self.prompt_count == 0:
            self.printError("cannot run cpyall when there are no responses")
            return
        last_resp = self.msg_hist[-1]["content"]
        pyperclip.copy(last_resp)
        self.console.print(f"[bright_black]Copied text to keyboard...[/]")


    def queryUser(self):
        self.console.print(
            f"[yellow]|{self.prompt_count}|[/][bold green] Input [/bold green][bold gray]> [/bold gray]",
            end="",
        )
        user_in = prompt().strip()
        if user_in == "":
            self.printError("user input is empty")
        elif user_in[0] == '!':
            raw_cmd = user_in.split('!')
            raw_cmd = raw_cmd[1:]
            for i in range(len(raw_cmd)):
                each_cmd = raw_cmd[i].strip().lower()

                tokens = each_cmd.split(' ')
                cmd = tokens[0]
                args = tokens[1:]

                self.runCommand(cmd, args)
        else:
            return user_in

    def runCommand(self, cmd, args=None):
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
            elif cmd == "copy" or cmd == "c":
                self.copyAll()
            elif cmd == "new" or cmd == "n":
                self.msg_hist = self.msg_hist[:1]
                self.prompt_count = 0
                self.printBanner()
            elif cmd == "run" or cmd == "r":
                if not hasattr(self, "agent"):
                    self.printError("agent not set, use the 'set' command to set the agent and application")
                else:
                    self.agent.runPrompt(args)
            elif cmd == "app":
                application_name = args[0]
                self.application_name = application_name
                print(f"Application set to: {application_name}")
            elif cmd == "agent":
                agent_name = args[0]
                if agent_name == "high-level":
                    self.agent = HighLevelAgent(self)
                    print(f"Agent set to: {agent_name}")
                elif agent_name == "fine-granular-types":
                    self.agent = FineGranularTypesAgent(self)
                    print(f"Agent set to: {agent_name}")
                elif agent_name == "fine-granular-attributes":
                    self.agent = FineGranularAttributesAgent(self)
                    print(f"Agent set to: {agent_name}")
                else:
                    self.printError(f"Agent {agent_name} not found")
        else:
            self.printError(
                f"!{cmd} in not in the list of commands, type !help"
            )


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
            f"[bright_black]Type '!quit' to quit the program; '!help' for a list of cmds[/]\n"
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
                                    addToFunctionName2Arguments(function_name, function_arguments, function_name_2_arguments)

                                function_name = tool_call.function.name

                                full_reply_content_shortened += "Function: " + function_name + "\n"
                                function_arguments = ""

                    if chunk_message.content is not None:
                        log += f"textual answer\n"
                        log += f"content: {chunk_message.content}\n"
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
            addToFunctionName2Arguments(function_name, function_arguments, function_name_2_arguments)

        self.saveFunctionCalls(function_name_2_arguments, full_reply_content_shortened)
        self.function_name_2_arguments = function_name_2_arguments

        self.console.print(md)
        self.console.print()
        self.msg_hist.append({"role": "assistant", "content": full_reply_content_shortened})

        if self.agent is not None:
            self.agent.applyFunctionCalls()

    def saveFunctionCalls(self, function_name_2_arguments, full_reply_content):
        if full_reply_content:
            file_name = f"{get_file_name(self.save_path)}-text.md"
            with open(Path(self.save_path) / file_name, "w") as f:
                f.write(full_reply_content)

        if function_name_2_arguments:
            for function_name, arguments in function_name_2_arguments.items():
                if function_name is not None and arguments is not None:
                    for argument in arguments:
                        file_name = f"{get_file_name(self.save_path)}-{function_name}.json"
                        with open(Path(self.save_path) / file_name, "w") as f:
                            json_object = json.loads(argument)
                            json.dump(json_object, f, indent=4)


    def init(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key == None or self.api_key == "":
            self.printError("the OPENAI_API_KEY environment variable is missing")
            sys.exit()

        if(self.config_selected == "AZURE_CONFIG"):
            self.client = AzureOpenAI(
                api_version = self.config[self.config_selected]["ApiVersion"],
                azure_endpoint = self.config[self.config_selected]["AZURE_OPENAI_ENDPOINT"],
                azure_deployment = self.config[self.config_selected]["AZURE_DEPLOYMENT"],
                api_key = self.config[self.config_selected]["AZURE_OPENAI_API_KEY"]
            )
        elif(self.config_selected == "OPENAI_CONFIG"):
            self.client = openai
            openai.api_key = self.config[self.config_selected]["API_KEY"]