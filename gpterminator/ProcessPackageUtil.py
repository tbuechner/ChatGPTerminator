import json
from xml.etree import ElementTree as ET

import yaml

from tokenizer import count_tokens_in_file


def remove(root, parent_map, xpath):
    # Find elements by XPath and remove them
    for target in root.findall(xpath):
        p = parent_map[target]  # Get the parent element from the map
        p.remove(target)  # Remove the target element from its parent


def is_empty(element):
    if element.attrib:
        return False
    return (not element.text or element.text.isspace()) and not element.tail and len(element) == 0


def remove_empty_elements(element, parent=None):
    # Recursively check all children of the current element
    for child in list(element):
        remove_empty_elements(child, element)

    # If the element is empty and it's not the root element, remove it
    if parent is not None and is_empty(element):
        # generate a string representation of the element
        element_str = ET.tostring(element, encoding='utf-8', method='xml').decode('utf-8')
        # print("Removing empty element: " + element_str)
        parent.remove(element)

    # If the element is equals to "{}", remove it
    if element.text == "{}":
        parent.remove(element)


def write_compressed_to_file(root, file_name):
    # Convert the XML tree to a string
    xml_string = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')

    with open(file_name + '-pretty.xml', 'w') as file:
        file.write(xml_string)

    # Remove all line breaks and extra spaces
    compressed_xml_string = xml_string.replace('\n', '').replace('\t', '').replace('  ', '')
    # Save the compressed XML string to a file
    with open(file_name + '-compressed.xml', 'w') as file:
        file.write(compressed_xml_string)


def write_json_to_file(folder_name, file_name, o, omit_pretty_json=False):
    if not omit_pretty_json:
        with open(folder_name + '/' + file_name + '-pretty.json', 'w') as f:
            f.write(json.dumps(o, indent=4))
    with open(folder_name + '/' + file_name + '-compressed.json', 'w') as f:
        f.write(json.dumps(o, separators=(',', ':')))

    with open(folder_name + '/' + file_name + '-pretty.yaml', 'w') as f:
        f.write(yaml.dump(o))


def write_to_file(folder_name, file_name, content):
    with open(folder_name + '/' + file_name, 'w') as f:
        f.write(content)


def write_token_count(f, folder_name, file_name):
    f.write("tokens " + file_name + ": " + str(count_tokens_in_file(folder_name + "/" + file_name)))
    f.write("\n")
