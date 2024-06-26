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

def renderTemplate(template_file, args=None):
    # Read the template file
    with open(template_file, "r") as file:
        template_string = file.read()

    # Create a template object
    template = Template(template_string)

    # if args is null or empty, create an empty dictionary
    if args is None:
        args = {}

    # if args does not have the key 'load_file', add it
    if 'load_file' not in args:
        args['load_file'] = loadFile

    rendered_string = template.render(args)

    return rendered_string

def loadFile(file_path):
    # Read the contents of the file
    with open(file_path, "r") as file:
        return file.read()

def generateFolderIfNotExists(folder_name_generated):
    if os.path.exists(folder_name_generated):
        os.system("rm -r " + folder_name_generated)

    # create folder folder_name_generated
    os.mkdir(folder_name_generated)
