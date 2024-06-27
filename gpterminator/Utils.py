import json
import os
import re

from jinja2 import Template

import xml.etree.ElementTree as ET

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


def createEmptyFileIfNotExists(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            json.dump([], file, indent=4)


def remove_characters_between_xml_elements(elem):
    """
    Recursively remove all characters between XML elements.

    Parameters:
    - elem: The XML element to process.
    """
    if len(elem):
        elem.text = None
        elem.tail = None
        for child_elem in elem:
            remove_characters_between_xml_elements(child_elem)
    else:
        if elem.tail:
            elem.tail = None


def pretty_print_xml(elem, level=0, indentation="  "):
    """
    Recursively print an XML element with indentation for pretty formatting.

    Parameters:
    - elem: The XML element to print.
    - level: The current level in the tree (used for indentation).
    - indentation: The string used for indentation, defaulting to two spaces.
    """
    indent = "\n" + level * indentation
    child_indent = "\n" + (level + 1) * indentation

    # Handling element text
    if len(elem) > 0 or elem.text:  # If the element has children or text
        if not elem.text or not elem.text.strip():
            elem.text = child_indent if len(elem) > 0 else ""
    else:  # Element has no children and no text
        if level > 0 and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent
        return  # No further processing for truly empty elements

    # Iterating through children if any
    for child in list(elem):
        pretty_print_xml(child, level + 1, indentation)

    # Adjusting tail for the last child
    if len(elem) > 0:
        if not elem[-1].tail or not elem[-1].tail.strip():
            elem[-1].tail = indent

    # Handling tail text for this element
    if level > 0 and (not elem.tail or not elem.tail.strip()):
        elem.tail = indent


def get_parent_map(root):
    return {c: p for p in root.iter() for c in p}


def remove_tags(element, tag_name, allowed_parent_tags):
    # Helper function to determine if the parent tag is in the allowed list
    def is_allowed_parent(parent):
        return parent.tag in allowed_parent_tags

    # Main logic to remove tags
    for child in list(element):
        if child.tag == tag_name and is_allowed_parent(element):
            parent = element
            index = list(parent).index(child)
            for subchild in list(child):
                parent.insert(index, subchild)
                index += 1
            parent.remove(child)
        # Recursively apply the function to child elements
        remove_tags(child, tag_name, allowed_parent_tags)
