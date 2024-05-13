import os
import re

from jinja2 import Template


def get_file_name(save_path):
    pattern = r'^\d{4}-'
    max_file_number = 0
    for idx, file_name in enumerate(os.listdir(f"{save_path}")):
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

def renderTemplate(template_file, types=None, application_name=None):
    # Read the template file
    with open(template_file, "r") as file:
        template_string = file.read()

    # Create a template object
    template = Template(template_string)

    # Render the template with the file contents
    rendered_string = template.render(
        load_file=loadFile,
        types=types,
        application_name=application_name
    )

    return rendered_string

def loadFile(file_path):
    # Read the contents of the file
    with open(file_path, "r") as file:
        return file.read()

def addToFunctionName2Arguments(function_name, function_arguments, function_name_2_arguments):
    if function_name in function_name_2_arguments:
        function_name_2_arguments[function_name].append(function_arguments)
    else:
        function_name_2_arguments[function_name] = [function_arguments]
