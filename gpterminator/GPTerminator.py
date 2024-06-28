import configparser
import json
import os
import sys
import time

import openai
import pyperclip
import tiktoken
from prompt_toolkit import prompt
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

import xml.etree.ElementTree as ET

from dicttoxml import dicttoxml

from openai.lib.azure import AzureOpenAI

from gpterminator.Choice import FunctionCall, Textual, addTextualChoice, addFunctionCall
from gpterminator.CompareAgent import CompareAgent
from gpterminator.FineGranularAttributesAgent import FineGranularAttributesAgent
from gpterminator.FineGranularTypesAgent import FineGranularTypesAgent
from gpterminator.HighLevelAgent import HighLevelAgent
from gpterminator.SummarizeAttributeAgent import SummarizeAttributeAgent
from gpterminator.SummarizeTypeAgent import SummarizeTypeAgent
from gpterminator.Utils import pretty_print_xml, get_parent_map, remove_tags


def rewrite_items_to_elements(root_elem, identifier, item_tag_name, element_name):
    parent_map = get_parent_map(root_elem)
    for each in root_elem.findall(identifier):
        # find child tags with tag 'item'
        names = []
        items = each.findall(item_tag_name)
        for item in items:
            names.append(item.text)

        constraint_factory = parent_map[each]
        constraint_factory.remove(each)

        for name_ in names:
            # add a new child tag with tag 'targetInternalTypeName' and text name_
            new_element = ET.SubElement(constraint_factory, element_name)
            new_element.text = name_


def rewrite_element_to_attribute(root_elem, identifier, element_name, attribute_name):
    for cf in root_elem.findall(identifier):
        type_element = cf.find(element_name)
        cf_type = type_element.text
        cf.set(attribute_name, cf_type)
        cf.remove(type_element)


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
            "set-agent": ["agent", "set the agent to use"],
            "set-application": ["app", "set the application to work on"],
            "data-model-high-level": ["dm-hl", "run the high-level data model creation process"],
            "data-model-fine-granular": ["dm-fg", "generate fine-granular data model from high-level data model"],
            "data-model-full-process": ["dm-fp", "full data model creation process"],
            "summarize-data-model": ["sum", "summarize the data model"],
            "compare-data-model": ["comp", "compare the high-level data models"],
            "generate-package": ["pkg", "generate a package"]
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
                if not (hasattr(self, "agent") or hasattr(self, "application_name")):
                    self.printError("agent or application not set")
                else:
                    self.agent.runPrompt(args)
            elif cmd == "set-application" or cmd == "app":
                application_name = args[0]
                self.application_name = application_name
                print(f"Application set to: {application_name}")
            elif cmd == "set-agent" or cmd == "agent":
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
            elif cmd == "data-model-full-process" or cmd == "dm-fp":
                if not hasattr(self, "application_name"):
                    self.printError("application not set")
                else:
                    if self.runHighLevelDataModelCreationProcess():
                        self.runFineGranularDataModelCreationProcess()
            elif cmd == "data-model-fine-granular" or cmd == "dm-fg":
                if not hasattr(self, "application_name"):
                    self.printError("application not set")
                else:
                    self.runFineGranularDataModelCreationProcess()
            elif cmd == "data-model-high-level" or cmd == "dm-hl":
                if not hasattr(self, "application_name"):
                    self.printError("application not set")
                else:
                    self.runHighLevelDataModelCreationProcess()
            elif cmd == "summarize-data-model" or cmd == "sum":
                if not hasattr(self, "application_name"):
                    self.printError("application not set")
                else:
                    self.summarizeDataModel()
            elif cmd == "compare-data-model" or cmd == "comp":
                if not hasattr(self, "application_name"):
                    self.printError("application not set")
                else:
                    self.agent = CompareAgent(self)
                    print(f"Agent set to: {self.agent.agent_name}")
                    self.agent.runPrompt(args)
            elif cmd == "generate-package" or cmd == "pkg":
                if not hasattr(self, "application_name"):
                    self.printError("application not set")
                else:
                    self.generatePackage()
        else:
            self.printError(
                f"!{cmd} in not in the list of commands, type !help"
            )


    def summarizeDataModel(self):
        self.agent = SummarizeTypeAgent(self)
        with open('applications/' + self.application_name + '/types-detailed.json', 'r') as file:
            types_detailed = json.load(file)
            # create a deep copy of types_detailed
            types_detailed_attributes = json.loads(json.dumps(types_detailed))
        # iterate over types_detailed and maintain an index
        for i in range(len(types_detailed)):
            type_ = types_detailed[i]
            # remove the attribute 'attributes' from type_
            type_.pop('attributes', None)
            self.agent.runPrompt(type_)
            if not self.agent.wasSuccessful():
                print("Summarize type agent was not successful")
            else:
                print("Summarize type agent was successful")

        self.agent = SummarizeAttributeAgent(self, self.agent.summarized_types)

        for i in range(len(types_detailed_attributes)):
            type_ = types_detailed_attributes[i]
            for attribute in type_['attributes']:
                self.agent.runPrompt([attribute, i])
                if not self.agent.wasSuccessful():
                    print("Summarize attribute agent was not successful")
                    return
                else:
                    print("Summarize type agent was successful")

        self.agent.saveSummary()


    def runHighLevelDataModelCreationProcess(self):
        self.agent = HighLevelAgent(self)
        print(f"Agent set to: {self.agent.agent_name}")
        self.agent.runPrompt()
        if not self.agent.wasSuccessful():
            print("High-level agent was not successful")
        else:
            print("High-level agent was successful")
        return self.agent.wasSuccessful()


    def runFineGranularDataModelCreationProcess(self):
        self.agent = FineGranularTypesAgent(self)
        print(f"Agent set to: {self.agent.agent_name}")
        self.agent.runPrompt()
        if not self.agent.wasSuccessful():
            print("Fine-granular types agent was not successful")
            return False
        else:
            self.agent = FineGranularAttributesAgent(self)
            print(f"Agent set to: {self.agent.agent_name}")
            number_of_types = self.agent.getNumberOfTypes()
            for i in range(number_of_types):
                print(f"Running agent on type {i}")
                args = [str(i)]
                self.agent.runPrompt(args)
                if not self.agent.wasSuccessful():
                    return False
            print("Fine-granular attributes agent was successful")
            return True

    def generatePackage(self):
        types_detailed_file_name = 'applications/' + self.application_name + '/types-detailed.json'
        with open(types_detailed_file_name, 'r') as file:
            types_detailed = json.load(file)

        types_rewritten = {
            'types': []
        }

        for type_ in types_detailed:
            types_rewritten['types'].append({
                'typeDef': type_
            })
            new_attributes = []
            for attribute in type_['attributes']:
                new_attributes.append({
                    'attributes': attribute
                })

                multiplicity = attribute['multiplicity']
                del attribute['multiplicity']

                constraint = attribute['constraint']
                attribute_type = constraint['attributeType']

                def getAttributeDefClass(multiplicity, single_class, multi_class):
                    if 'exactlyOne' == multiplicity or 'maximalOne' == multiplicity:
                        return single_class
                    else:
                        return multi_class


                if 'string' == attribute_type:
                    constraint_factory_type = 'stringConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')
                if 'longText' == attribute_type:
                    constraint_factory_type = 'longConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')
                if 'textEnumeration' == attribute_type:
                    constraint_factory_type = 'textEnumerationConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')
                if 'numberEnumeration' == attribute_type:
                    constraint_factory_type = 'numberEnumerationConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleNumberAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiNumberAttributeDef')
                if 'reference' == attribute_type:
                    constraint_factory_type = 'referenceConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleReferenceAttributeDef$SingleCustomReferenceAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiReferenceAttributeDef$MultiCustomReferenceAttributeDef')
                if 'date' == attribute_type:
                    constraint_factory_type = 'dateConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleDateAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiDateAttributeDef')
                if 'number' == attribute_type:
                    constraint_factory_type = 'numberConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleNumberAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiNumberAttributeDef')
                if 'boolean' == attribute_type:
                    constraint_factory_type = 'booleanConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleBooleanAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiBooleanAttributeDef')
                if 'richString' == attribute_type:
                    constraint_factory_type = 'richStringConstraint'
                    attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleRichStringAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiRichStringAttributeDef')

                if constraint_factory_type is None:
                    print(f"ERROR: No constraint factory type found for attribute type {attribute_type}")

                target_internal_type_names = constraint.get('targetInternalTypeNames', None)
                target_entity_class = constraint.get('targetEntityClass', None)
                is_hierarchy = constraint.get('isHierarchy', None)

                date_specificity = constraint.get('specificity', None)
                date_format = constraint.get('dateFormat', None)

                precision = constraint.get('precision', None)
                localizedTextAfterSupplier = constraint.get('localizedTextAfterSupplier', None)

                elements = constraint.get('elements', None)

                del attribute['constraint']

                cf_node = {
                    'multiplicity': {
                        'key': multiplicity
                    },
                    'type': constraint_factory_type,
                    'attributeDefClass': attribute_def_class
                }

                attribute['constraintFactory'] = cf_node

                if target_internal_type_names is not None:
                    cf_node['typeNames'] = target_internal_type_names
                if target_entity_class is not None:
                    cf_node['entityClass'] = target_entity_class
                if is_hierarchy is not None:
                    cf_node['isHierarchy'] = is_hierarchy
                    cf_node['sameWorkspace'] = True

                if date_specificity is not None:
                    cf_node['specificity'] = date_specificity
                if date_format is not None:
                    cf_node['dateFormat'] = date_format

                if precision is not None:
                    cf_node['precision'] = precision
                if localizedTextAfterSupplier is not None:
                    cf_node['localizedTextAfterSupplier'] = localizedTextAfterSupplier

                if elements is not None:
                    values = []
                    localized_names = []
                    for element in elements:
                        value = element.get('value')
                        values.append(value)
                        localized_name = element.get('localizedName')
                        # iterate over all keys of localized_name
                        localizations = []
                        for key in localized_name.keys():
                            localizations.append({
                                'key': key,
                                'value': {
                                    'value': localized_name[key],
                                    'language': key
                                }
                            })

                        localized_names.append({
                            'key': value,
                            'value': {
                                'localizations': localizations
                            }
                        })

                    cf_node['elements'] = values
                    cf_node['element2localizedLabel'] = localized_names


            type_['attributesWrapper'] = new_attributes
            del type_['attributes']

        new_root = {
            "xmlVersion": "1.8",
            "package": {
                "internalName": "cf.cplace.template.okr",
                "version": "10",
                "name": {
                    "de": "Solution Template - Objectives & Key Results",
                    "en": "Solution Template - Objectives & Key Results"
                },
                "cplaceRelease": "24.1",
                "publishDate": "2024-01-25T14:49:25.893+01:00",
                "slots": {
                    "slot": {
                        "internalName": "cf.cplace.okr.okr",
                        "name": {
                            "de": "Objectives Key Results",
                            "en": "Objectives Key Results"
                        },
                        "workspace": {
                            "name": "OKR",
                            "apps": ["cf.cplace.platform"],
                            "rootPage": {
                                "page": {
                                    "name": "Root Page",
                                    "id": "xaji0y6dpbhsahxthv3a3zmf8",
                                    "custom": {
                                        "type": "default.page",
                                        "attributes": {}
                                    },
                                    "widgetContainer": {
                                        "widgetsLayout": {},
                                        "widgets": {}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "maps": {}
        }

        new_root['package']['slots']['slot']['workspace']['types'] = types_rewritten['types']

        with open('applications/' + self.application_name + '/types-detailed-rewritten.json', 'w') as file:
            json.dump(new_root, file, indent=4)

        xml_bytes = dicttoxml(new_root, attr_type=False, custom_root='solutionManagement')

        root_elem = ET.fromstring(xml_bytes)

        remove_tags(root_elem, 'attributesWrapper', ['typeDef'])
        remove_tags(root_elem, 'item', ['types'])
        remove_tags(root_elem, 'item', ['typeDef'])

        rewrite_element_to_attribute(root_elem, './/constraintFactory', 'type', 'type')

        xml_version_element = root_elem.find('xmlVersion')
        root_elem.set('xmlVersion', xml_version_element.text)
        root_elem.remove(xml_version_element)

        rewrite_element_to_attribute(root_elem, './/package', 'internalName', 'internalName')
        rewrite_element_to_attribute(root_elem, './/package', 'version', 'version')
        rewrite_element_to_attribute(root_elem, './/slot', 'internalName', 'internalName')

        rewrite_items_to_elements(root_elem, './/constraintFactory/typeNames', 'item', 'typeNames')
        rewrite_items_to_elements(root_elem, './/constraintFactory/elements', 'item', 'elements')

        for each in root_elem.findall('.//element2localizedLabel/item'):
            each.tag = 'entry'

        for each in root_elem.findall('.//localizations/item'):
            each.tag = 'entry'

        pretty_print_xml(root_elem)

        # Convert the ElementTree to a string
        xml_str = ET.tostring(root_elem, encoding='unicode')

        # save the XML string to a file
        with open('applications/' + self.application_name + '/export.xml', 'w') as file:
            file.write(xml_str)

        # zip export.xml into package.zip
        os.system("zip -j " + 'applications/' + self.application_name + "/package.zip " + 'applications/' + self.application_name + "/export.xml")

        pass


    def printBanner(self):
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

        self.choices = []

        panel_content = ""
        log = ""

        with Live(md, console=self.console, transient=True) as live:
            for chunk in resp:
                for choice in chunk.choices:
                    chunk_message = choice.delta  # extract the message

                    if(chunk_message.tool_calls):
                        for tool_call in chunk_message.tool_calls:
                            log += f"tool_call\n"
                            function_call_arguments = tool_call.function.arguments
                            log += f"function_call_arguments: {function_call_arguments}\n"

                            panel_content += addFunctionCall(self.choices, chunk.id, tool_call.function.name, function_call_arguments)

                    if chunk_message.content is not None:
                        log += f"textual answer\n"
                        log += f"content: {chunk_message.content}\n"
                        panel_content += addTextualChoice(self.choices, chunk.id, chunk_message.content)

                    encoding = tiktoken.encoding_for_model(self.model)
                    num_tokens = len(encoding.encode(panel_content))
                    time_elapsed_s = time.time() - start_time
                    subtitle_str = f"[bright_black]Tokens:[/] [bold red]{num_tokens}[/] | "
                    subtitle_str += (
                        f"[bright_black]Time Elapsed:[/][bold yellow] {time_elapsed_s:.1f}s [/]"
                    )
                    md = Panel(
                        Markdown(panel_content, self.code_theme),
                        border_style="bright_black",
                        title="[bright_black]Assistant[/]",
                        title_align="left",
                        subtitle=subtitle_str,
                        subtitle_align="right",
                    )
                    live.update(md)

        # print("choices: " + str(self.choices))
        for choice in self.choices:
            choice.save(self.save_path)

        self.console.print(md)
        self.console.print()

        for choice in self.choices:
            self.msg_hist.append(choice.getMsgForHistory())

        if self.agent is not None:
            self.agent.applyFunctionCalls()

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


def createPackage():
    # Create the new XML structure
    package = ET.Element("package", xmlVersion="1.8")
    inner_package = ET.SubElement(package, "package", internalName="cf.cplace.template.okr", version="10")

    name = ET.SubElement(inner_package, "name")
    ET.SubElement(name, "de").text = "Solution Template - Objectives & Key Results"
    ET.SubElement(name, "en").text = "Solution Template - Objectives & Key Results"

    ET.SubElement(inner_package, "cplaceRelease").text = "24.1"
    ET.SubElement(inner_package, "publishDate").text = "2024-01-25T14:49:25.893+01:00"

    slots = ET.SubElement(inner_package, "slots")
    attribute = ET.SubElement(slots, "slot", internalName="cf.cplace.okr.okr")

    slot_name = ET.SubElement(attribute, "name")
    ET.SubElement(slot_name, "de").text = "Objectives Key Results"
    ET.SubElement(slot_name, "en").text = "Objectives Key Results"

    workspace = ET.SubElement(attribute, "workspace")
    ET.SubElement(workspace, "name").text = "OKR"

    return package
