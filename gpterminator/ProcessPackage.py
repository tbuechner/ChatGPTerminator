import json
import os
import string
import xml
import random

from xml.dom import minidom

import xml.etree.ElementTree as ET
import xmltodict

import textwrap

from ProcessPackageUtil import remove, remove_empty_elements, write_json_to_file, write_token_count
from gpterminator.ProcessWidgets import find_all_widgets, rewrite_widgets, count_widget_kinds, condense_widgets, \
    write_widgets_per_type


def process_pkg(application_name):
    folder_name = 'applications/' + application_name

    folder_name_generated = 'applications/' + application_name + '/generated'

    print("processing folder: " + folder_name)

    # delete folder folder_name_generated if it exists with all its content
    if os.path.exists(folder_name_generated):
        os.system("rm -r " + folder_name_generated)

    # create folder folder_name_generated
    os.mkdir(folder_name_generated)

    type_name_2_attribute_names = get_type_name_2_attribute_names(folder_name)

    # Load and parse the XML document
    tree = ET.parse(folder_name + '/export.xml')
    root = tree.getroot()

    write_slot_and_type_names(root, folder_name_generated, 'slots-and-types-all', './/typeDef', lambda slot: slot.get('internalName'))

    slots_to_be_retained = get_slots_to_be_retained(folder_name)

    write_type_and_attribute_names(root, folder_name_generated, 'types-and-attributes-all', './/types/typeDef', '-')

    parent_map = get_parent_map(root)

    remove_slots(root, parent_map, slots_to_be_retained)

    widgets = find_all_widgets(root, parent_map)

    # print("Widgets: ", widgets)
    write_json_to_file(folder_name_generated, "widgets", widgets)

    rewrite_widgets(widgets)
    write_json_to_file(folder_name_generated, "widgets-rewritten", widgets)
    write_json_to_file(folder_name_generated, "widgets-rewritten-first-3", widgets[:3])

    count_widget_kinds(widgets, folder_name_generated)

    condense_widgets(widgets)
    write_json_to_file(folder_name_generated, "widgets-condensed", widgets)

    widgets_folder_name = folder_name_generated + '/widgets-for-types'
    os.mkdir(widgets_folder_name)

    write_widgets_per_type(widgets, widgets_folder_name, folder_name_generated)

    remove_generic_elements(root, parent_map)

    rewrite(root, parent_map)

    parent_map = get_parent_map(root)

    remove_types_and_attributes(root, parent_map, type_name_2_attribute_names)

    write_slot_and_type_names(root, folder_name_generated, 'slots-and-types-after-removal', 'type', lambda slot: slot.find('internalName').text)

    remove_pages(root, parent_map, type_name_2_attribute_names)

    rewrite_pages(root, parent_map)

    remove_empty_elements(root)

    pretty_print_xml(root, 0)

    with open(folder_name_generated + '/after-page-removal.xml', 'w') as f:
        f.write(ET.tostring(root, encoding='unicode'))

    remove_all_pages(root)

    write_type_names(root, folder_name_generated, 'types-after-removal', './/type/name')
    write_attribute_names(root, folder_name_generated, 'attributes-after-removal', './/type/attributes/name')

    pretty_print_xml(root, 0)

    write_to_file(root, folder_name_generated, "thinned-out")

    # create a deep clone of root
    root_copy = ET.fromstring(ET.tostring(root))
    parent_map = get_parent_map(root_copy)
    rewrite_to_json(root_copy, parent_map, folder_name_generated, "rewritten")

    # create a deep clone of root
    root_copy = ET.fromstring(ET.tostring(root))
    parent_map = get_parent_map(root_copy)

    remove_to_basics(root_copy, parent_map)
    pretty_print_xml(root_copy, 0)
    write_to_file(root_copy, folder_name_generated, "basic-structure")

    write_token_counts(folder_name_generated)

    rewrite_to_pkg_format(root, tree)

    with open(folder_name_generated + '/export.xml', 'w') as f:
        f.write(ET.tostring(root, encoding='unicode'))

    # zip export.xml into package.zip
    os.system("zip -j " + folder_name_generated + "/package.zip " + folder_name_generated + "/export.xml")

def get_slots_to_be_retained(folder_name):
    with open(folder_name + '/slots-to-be-retained.txt') as f:
        slots_to_be_retained = f.read().splitlines()
    return slots_to_be_retained


def get_type_name_2_attribute_names(folder_name):
    with open(folder_name + '/types-and-attributes-to-be-retained.txt') as f:
        type_name_2_attribute_names = {}
        lines = f.read().splitlines()
        for line in lines:
            if not line.startswith('-'):
                if not line.startswith('\t'):
                    type_name = line
                    type_name_2_attribute_names[type_name] = []
                else:
                    type_name_2_attribute_names[type_name].append(line[1:])
    # print(type_name_2_attribute_names)
    return type_name_2_attribute_names


def get_parent_map(root):
    return {c: p for p in root.iter() for c in p}


def rewrite_to_json(root, parent_map, folder_name, file_name):
    remove_attribute(root, 'xmlVersion')
    remove_attribute(root, 'xmlns:xsi')
    remove_attribute(root, 'xsi:noNamespaceSchemaLocation')
    remove_attribute(root, '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation')

    name = root.find('./name')
    name.tag = 'localizedName'

    for slot in root.findall('.//slot'):
        # rename the tag 'slot' to 'slots'
        slot.tag = 'slots'

        name_ = slot.find('.name')
        name_.tag = 'localizedName'

        for type_ in slot.findall('.//type'):

            # rename the tag 'type' to 'types'
            type_.tag = 'types'

            for attribute in type_.findall('.//attributes'):
                # rename the tag 'attributes' to 'attributes'
                attribute.tag = 'attributes'

                for element in attribute.findall('.//element'):
                    # rename the tag 'element' to 'elements'
                    element.tag = 'elements'

    json_object = xmltodict.parse(ET.tostring(root, encoding='utf-8'), force_list=('slots', 'types', 'attributes', 'elements'))
    # write the json object to a file
    write_json_to_file(folder_name, file_name, json_object)


def remove_attribute(element, attribute_name):
    if attribute_name in element.attrib:
        del element.attrib[attribute_name]

def rewrite_to_pkg_format(root, tree):
    parent_map = get_parent_map(root)
    rewrite_to_pkg_format_add_mandatory_elements(root, parent_map)
    pretty_print_xml(root, 0)


def generate_pkgs():
    # for all files in folder 'generated-pkgs'
    folder_name = 'generated-pkgs'
    # do not walk the directory tree recursively, only on first level
    for file in os.listdir(folder_name):
        # if the file is a .zip file
        if file.endswith('.xml') and not file.endswith('-rewritten.xml'):
            # strip file of the extension
            file = file[:-4]

            pkg_folder_name = folder_name + '/' + file

            if os.path.exists(pkg_folder_name):
                os.system("rm -r " + pkg_folder_name)

            os.mkdir(pkg_folder_name)

            tree = ET.parse(folder_name + '/' + file + '.xml')
            root = tree.getroot()
            rewrite_to_pkg_format(root, tree)

            with open(pkg_folder_name + '/' + 'export.xml', 'w') as f:
                f.write(ET.tostring(root, encoding='unicode'))

            os.system("zip -j " + pkg_folder_name + "/" + file + ".zip " + pkg_folder_name + "/" + "export.xml")


def rewrite_to_pkg_format_add_mandatory_elements(root, parent_map):
    if 'xmlns:xsi' in root.attrib:
        del root.attrib['xmlns:xsi']
    if 'xsi:noNamespaceSchemaLocation' in root.attrib:
        del root.attrib['xsi:noNamespaceSchemaLocation']

    # add a new element with the tag 'package' to the root element
    package = ET.Element('package')

    # move all children of root under package
    for child in list(root):
        package.append(child)
        root.remove(child)

    root.append(package)

    internal_name = root.find('.//package/internalName')
    if internal_name is not None:
        package.set('internalName', internal_name.text)
        package.remove(internal_name)
    version = root.find('.//package/version')
    if version is not None:
        package.set('version', version.text)
        package.remove(version)

    add_element(package, 'cplaceRelease', '24.1')
    add_element(package, 'publishDate', '2024-01-25T14:49:25.893+01:00')

    add_element(root, 'maps')

    slots = add_element(root.find('.//package'), 'slots')

    parent_map = get_parent_map(root)

    for slot in root.findall('.//slot'):
        parent_map[slot].remove(slot)
        slots.append(slot)

    parent_map = get_parent_map(root)

    slots = root.findall('.//slot')
    for slot in slots:
        workspace = ET.Element('workspace')
        slot.append(workspace)
        workspace_name_element = ET.Element('name')
        slot_workspace_name_element = slot.find('workspaceName')
        if slot_workspace_name_element is not None:
            workspace_name = slot_workspace_name_element.text
            workspace_name_element.text = workspace_name
            workspace.append(workspace_name_element)
            slot.remove(slot_workspace_name_element)
        else:
            # print string representation of slot
            slot_str = ET.tostring(slot, encoding='utf-8', method='xml').decode('utf-8')
            print("slot without workspaceName: " + slot_str)

        slot_internal_name_element = slot.find('internalName')
        if slot_internal_name_element is not None:
            slot.set('internalName', slot_internal_name_element.text)
            slot.remove(slot_internal_name_element)

        new_types_element = ET.Element('types')
        workspace.append(new_types_element)

        parent_map = get_parent_map(root)

        types = slot.findall('.//type')
        for type_element in types:
            type_element.tag = 'typeDef'
            new_types_element.append(type_element)
            type_parent = parent_map[type_element]
            type_parent.remove(type_element)

    workspaces = root.findall('.//workspace')
    for workspace in workspaces:
        add_element(workspace, 'apps', '["cf.cplace.platform"]')

    for constraint in root.findall('.//constraint'):
        # read the value of the element with tag 'attributeType'
        attribute_type_element = constraint.find('.//attributeType')
        attribute_type = attribute_type_element.text

        if attribute_type == 'string':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'stringConstraint',
                'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')

        elif attribute_type == 'long':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'longConstraint',
                'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')

        elif attribute_type == 'number':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'numberConstraint',
                'cf.cplace.platform.assets.custom.def.SingleNumberAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiNumberAttributeDef')

        elif attribute_type == 'date':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'dateConstraint',
                'cf.cplace.platform.assets.custom.def.SingleDateAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiDateAttributeDef')

        elif attribute_type == 'richString':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'richStringConstraint',
                'cf.cplace.platform.assets.custom.def.SingleRichStringAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiRichStringAttributeDef')

        elif attribute_type == 'boolean':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'booleanConstraint',
                'cf.cplace.platform.assets.custom.def.SingleBooleanAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiBooleanAttributeDef')

        elif attribute_type == 'textEnumeration':
            constraint_factory = rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'textEnumerationConstraint',
                'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')

            rewrite_to_pkg_format_enumeration_values(constraint_factory)

        elif attribute_type == 'numberEnumeration':
            constraint_factory = rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'numberEnumerationConstraint',
                'cf.cplace.platform.assets.custom.def.SingleNumberAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiNumberAttributeDef')

            rewrite_to_pkg_format_enumeration_values(constraint_factory)

        elif attribute_type == 'localizedString':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'localizedStringConstraint',
                'cf.cplace.platform.assets.custom.def.SingleLocalizedStringAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiLocalizedStringAttributeDef')

        elif attribute_type == 'dynamicEnumeration':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'dynamicEnumerationConstraint',
                'cf.cplace.platform.assets.custom.def.SingleDynamicEnumerationAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiDynamicEnumerationAttributeDef')

        elif attribute_type == 'reference':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'referenceConstraint',
                'cf.cplace.platform.assets.custom.def.SingleReferenceAttributeDef$SingleCustomReferenceAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiReferenceAttributeDef$MultiCustomReferenceAttributeDef')

        elif attribute_type == 'color':
            rewrite_constraint_factory_to_pkg(
                constraint,
                parent_map,
                'colorConstraint',
                'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef',
                'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')

        else:
            print('Unknown attribute type: ' + attribute_type)

    type_defs = root.findall('.//typeDef')
    for type_def in type_defs:
        applies_to = ET.Element('appliesTo')
        type_def.append(applies_to)
        key = ET.Element('key')
        key.text = 'page'
        applies_to.append(key)

        localized_page_names_mode = ET.Element('localizedPageNamesMode')
        type_def.append(localized_page_names_mode)
        key = ET.Element('key')
        key.text = 'none'
        localized_page_names_mode.append(key)

        add_element(type_def, 'showNewButton', 'true')

    attributes = root.findall('.//attributes')
    for attribute in attributes:
        constraint_factory = attribute.find('.//constraintFactory')
        if constraint_factory is not None:
            if constraint_factory.get('type') == 'dynamicEnumerationConstraint':
                parent_map[attribute].remove(attribute)

    multiplicities = root.findall('.//multiplicity')
    for multiplicity in multiplicities:
        key = multiplicity.text
        # if key is not None
        if key is not None:
            key_element = ET.Element('key')
            key_element.text = key
            multiplicity.append(key_element)
            multiplicity.text = None

    workspaces = root.findall('.//workspace')
    for workspace in workspaces:
        root_page = ET.Element('rootPage')
        workspace.append(root_page)
        page = ET.Element('page')
        root_page.append(page)
        add_element(page, 'name', 'Root Page')

        # q: how to generate a random id, which is based on a seed and is deterministic?
        # a: use random.seed(seed) to set the seed

        random.seed(42)
        id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=25))
        add_element(page, 'id', id)

        custom = ET.Element('custom')
        page.append(custom)
        add_element(custom, 'type', 'default.page')
        attributes = ET.Element('attributes')
        custom.append(attributes)

        widget_container = ET.Element('widgetContainer')
        page.append(widget_container)
        widgets_layout = ET.Element('widgetsLayout')
        widget_container.append(widgets_layout)
        widgets = ET.Element('widgets')
        widget_container.append(widgets)


def rewrite_to_pkg_format_enumeration_values(constraint_factory):
    parent_map = get_parent_map(constraint_factory)
    element_to_icon = {}
    element_to_localized_names = {}

    # print text representation of constraint_factory
    # print(ET.tostring(constraint_factory, encoding='utf-8', method='xml').decode('utf-8'))

    for element in constraint_factory.findall('.//element'):

        # print("element: " + ET.tostring(element, encoding='utf-8', method='xml').decode('utf-8'))

        value = element.find('.//value').text

        new_element = ET.Element('elements')
        new_element.text = value
        constraint_factory.append(new_element)

        icon_element = element.find('.//icon')
        if icon_element is not None:
            icon = icon_element.text
            element_to_icon[value] = icon

        localized_names = []
        for localized_name in element.findall('.//localizedName'):
            # iterate over all children of localized_name
            for child in list(localized_name):
                language = child.tag
                label = child.text
                localized_names.append({language: label})
        element_to_localized_names[value] = localized_names

        parent_map[element].remove(element)
    new_element_to_icon = ET.Element('element2icon')
    constraint_factory.append(new_element_to_icon)
    for key, value in element_to_icon.items():
        entry = ET.Element('entry')
        new_element_to_icon.append(entry)
        key_element = ET.Element('key')
        key_element.text = key
        entry.append(key_element)
        value_element = ET.Element('value')
        value_element.text = value
        entry.append(value_element)
    new_element_to_localized_names = ET.Element('element2localizedLabel')
    constraint_factory.append(new_element_to_localized_names)
    for key, value in element_to_localized_names.items():
        entry = ET.Element('entry')
        new_element_to_localized_names.append(entry)
        key_element = ET.Element('key')
        key_element.text = key
        entry.append(key_element)
        value_element = ET.Element('value')
        entry.append(value_element)
        localizations = ET.Element('localizations')
        value_element.append(localizations)
        for localized_name in value:
            for key in localized_name:
                entry = ET.Element('entry')
                localizations.append(entry)
                key_element = ET.Element('key')
                key_element.text = key
                entry.append(key_element)
                value_element = ET.Element('value')

                value_language_element = ET.Element('language')
                value_language_element.text = key
                value_element.append(value_language_element)

                value_value_element = ET.Element('value')
                value_value_element.text = localized_name.get(key)
                value_element.append(value_value_element)

                entry.append(value_element)


def rewrite_constraint_factory_to_pkg(constraint, parent_map, constraint_name, single_def_class, multi_def_class):
    attribute = parent_map[constraint]
    constraint_factory = ET.Element('constraintFactory')
    constraint_factory.set('type', constraint_name)
    attribute.append(constraint_factory)
    multiplicity = attribute.find('.//multiplicity')
    constraint_factory.append(multiplicity)
    attribute.remove(multiplicity)
    attribute.remove(constraint)

    # move alle children of constraint to constraint_factory
    for child in list(constraint):
        if not child.tag == 'attributeType':
            constraint_factory.append(child)
            constraint.remove(child)

    # get child element with tag 'multiplicity'
    multiplicity = constraint_factory.find('.//multiplicity')
    key = multiplicity.find('.//key')
    if key is not None:
        if key.text == 'exactlyOne' or key.text == 'maximalOne':
            add_element(constraint_factory, 'attributeDefClass', single_def_class)
            return
    add_element(constraint_factory, 'attributeDefClass', multi_def_class)

    return constraint_factory


def add_element(package, element_name, text=None):
    new_element = ET.Element(element_name)
    if text is not None:
        new_element.text = text
    package.append(new_element)
    return new_element


def remove_types_and_attributes(root, parent_map, type_name_2_attribute_names):
    for type_ in root.findall('.//slot/type'):
        name_element = type_.find('.//name')
        type_name = name_element.text
        if type_name not in type_name_2_attribute_names:
            parent = parent_map[type_]
            parent.remove(type_)
        else:
            attribute_names = type_name_2_attribute_names[type_name]
            # if attribute_names has one element and this element is 'all'
            if len(attribute_names) == 0:
                pass
            else:
                attributes_to_be_removed = []
                for attribute in type_.findall('.//attributes'):
                    attribute_name = attribute.find('.//name').text
                    if attribute_name not in attribute_names:
                        attributes_to_be_removed.append(attribute)
                for attribute in attributes_to_be_removed:
                    type_.remove(attribute)


def rewrite(root, parent_map):
    root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    root.set('xsi:noNamespaceSchemaLocation', "../../package-thinned-out-schema.xsd")

    # move all children of root.package one level up
    package = root.find('.//package')

    # transfer all attributes of package to root
    for key, value in package.attrib.items():
        new_element = ET.Element(key)
        new_element.text = value
        package.append(new_element)

    for child in list(package):
        root.append(child)
        package.remove(child)
    root.remove(package)

    root.tag = 'package'

    parent_map = get_parent_map(root)

    workspaces = root.findall('.//workspace')
    for workspace in workspaces:
        slot = parent_map[workspace]
        workspace_name_element = workspace.find('.//name')
        workspace_name = workspace_name_element.text
        workspace.remove(workspace_name_element)
        slot.set('workspaceName', workspace_name)
        for child in list(workspace):
            slot.append(child)
            workspace.remove(child)

        slot.remove(workspace)

    parent_map = get_parent_map(root)

    slots = root.findall('.//slot')
    for slot in slots:
        internal_name = slot.get('internalName')
        workspace_name = slot.get('workspaceName')
        internal_name_element = ET.Element('internalName')
        internal_name_element.text = internal_name
        del slot.attrib['internalName']

        slot.append(internal_name_element)
        workspace_name_element = ET.Element('workspaceName')
        workspace_name_element.text = workspace_name
        slot.append(workspace_name_element)
        del slot.attrib['workspaceName']

    for type_def in root.findall('.//typeDef'):
        types = parent_map[type_def]
        slot = parent_map[types]
        slot.append(type_def)
        types.remove(type_def)
        type_def.tag = 'type'

    parent_map = get_parent_map(root)

    types_elements = root.findall('.//types')
    for types in types_elements:
        slot = parent_map[types]
        slot.remove(types)

    parent_map = get_parent_map(root)

    element2localized_labels = {}
    element2icon = {}
    elements = []

    for element_to_icon in root.findall('.//element2icon/entry'):
        element = element_to_icon.find('.//key').text
        icon = element_to_icon.find('.//value').text
        element2icon[element] = icon

    for element_to_icon in root.findall('.//element2icon'):
        parent_map[element_to_icon].remove(element_to_icon)

    for element_to_localized_label in root.findall('.//element2localizedLabel/entry'):
        element = element_to_localized_label.find('.//key').text
        localized_labels = []
        for entry in element_to_localized_label.findall('.//value/localizations/entry'):
            language = entry.find('.//key').text
            label = entry.find('.//value/value').text
            localized_label = {language: label}
            localized_labels.append(localized_label)
        element2localized_labels[element] = localized_labels
        parent_map[element_to_localized_label].remove(element_to_localized_label)

    for element_to_localized_label in root.findall('.//element2localizedLabel'):
        parent_map[element_to_localized_label].remove(element_to_localized_label)

    for element in root.findall('.//constraintFactory[@type="textEnumerationConstraint"]/elements'):
        rewrite_enumeration_element(element, element2icon, element2localized_labels, elements, icon, localized_labels, parent_map)

    for element in root.findall('.//constraintFactory[@type="numberEnumerationConstraint"]/elements'):
        rewrite_enumeration_element(element, element2icon, element2localized_labels, elements, icon, localized_labels, parent_map)

    # print(elements)
    # print(element2icon)
    # print(element2localized_labels)

    multiplicities = root.findall('.//multiplicity')
    for multiplicity in multiplicities:
        key = multiplicity.find('.//key')
        if key is None:
            multiplicity.text = 'anyNumber'
        else:
            multiplicity.text = key.text
            # remove the tag `key`
            multiplicity.remove(key)

        constraint = parent_map[multiplicity]
        attribute = parent_map[constraint]
        # move the multiplicity element to the attribute element
        attribute.append(multiplicity)
        constraint.remove(multiplicity)

        constraint_factories = root.findall('.//constraintFactory')
        for constraint_factory in constraint_factories:
            constraint_factory.tag = 'constraint'
            constraint_type = constraint_factory.get('type')
            # remove the suffix 'Constraint' from the constraint_type
            constraint_type = constraint_type[:-10]
            add_element(constraint_factory, 'attributeType', constraint_type)
            del constraint_factory.attrib['type']

    # move slots one level up
    for slot in root.findall('.//slot'):
        root.append(slot)

    for slots in root.findall('.//slots'):
        root.remove(slots)


def rewrite_enumeration_element(element, element2icon, element2localized_labels, elements, icon, localized_labels, parent_map):
    element_value = element.text
    elements.append(element_value)
    # if element_value is in element2icon
    if element_value in element2icon:
        icon = element2icon[element_value]
    if element_value in element2localized_labels:
        localized_labels = element2localized_labels[element_value]
        # print(localized_labels)
    new_element = ET.Element('element')
    new_value = ET.Element('value')
    new_value.text = element_value
    new_element.append(new_value)
    if icon is not None:
        add_element(new_element, 'icon', icon)
    if localized_labels is not None:
        new_localized_name = ET.Element('localizedName')
        for localized_label in localized_labels:
            # iterate over all keys of localized_label
            for key in localized_label:
                new_localization = ET.Element(key)
                new_localization.text = localized_label.get(key)
                new_localized_name.append(new_localization)
        new_element.append(new_localized_name)
        # print(new_localized_name)
    parent_map[element].append(new_element)
    parent_map[element].remove(element)

    # print a textual representation of the element
    # print(ET.tostring(element, encoding='utf-8', method='xml').decode('utf-8'))


def remove_slots(root, parent_map, slots_to_be_retained):
    for slot in root.findall('.//slot'):
        internal_name = slot.get('internalName')
        if internal_name not in slots_to_be_retained:
            slot_parent = parent_map[slot]
            parent = root if slot_parent is None else slot_parent
            parent.remove(slot)


def write_token_counts(folder_name):
    with open(folder_name + '/' + 'token-counts.txt', 'w') as f:
        write_token_count(f, folder_name, "thinned-out.xml")
        write_token_count(f, folder_name, "thinned-out-compressed.xml")
        write_token_count(f, folder_name, "after-page-removal.xml")
        write_token_count(f, folder_name, "basic-structure.xml")
        write_token_count(f, folder_name, "basic-structure-compressed.xml")


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


def write_slot_and_type_names(root, folder_name_generated, file_name, find_type_xpath, get_slot_name_func):
    slot_2_type_names = {}
    for slot in root.findall('.//slot'):
        # read attribute 'internalName' of slot
        slot_name = get_slot_name_func(slot)
        type_names = []
        for type_ in slot.findall(find_type_xpath):
            type_name = type_.find('.//name').text
            type_names.append(type_name)
        slot_2_type_names[slot_name] = type_names
    # print(slot_2_type_names)
    with open(folder_name_generated + '/' + file_name + '.txt', 'w') as f:
        for slot_name in slot_2_type_names:
            f.write(slot_name + "\n")
            for type_name in slot_2_type_names[slot_name]:
                f.write("\t" + type_name + "\n")


def write_type_and_attribute_names(root, folder_name, file_name, xpath, prefix=''):
    type_names = []
    type_2_attribute_names = {}
    for type_element in root.findall(xpath):
        name_element = type_element.find('.//name')
        type_name = name_element.text
        if type_name not in type_names:
            type_names.append(type_name)

        for attribute_name_element in type_element.findall('.//attributes/name'):
            attribute_name = attribute_name_element.text
            if type_name not in type_2_attribute_names:
                type_2_attribute_names[type_name] = []
            if attribute_name not in type_2_attribute_names[type_name]:
                type_2_attribute_names[type_name].append(attribute_name)

    type_names.sort()
    # print(type_names)
    # print(type_2_attribute_names)

    with open(folder_name + '/' +  file_name + '.txt', 'w') as f:
        for type_name in type_names:
            f.write(prefix + type_name + "\n")
            if type_name in type_2_attribute_names:
                for attribute_name in type_2_attribute_names[type_name]:
                    f.write("\t" + attribute_name + "\n")


def write_type_names(root, folder_name, file_name, xpath, prefix=''):
    type_names = []
    for name in root.findall(xpath):
        # only append if not in type_names
        if name.text not in type_names:
            type_names.append(name.text)

    # sort the list of type names
    type_names.sort()

    with open(folder_name + '/' +  file_name + '.txt', 'w') as f:
        for item in type_names:
            # prepend prefix to item
            f.write(prefix + item + "\n")


def write_to_file(root, folder_name, file_name):
    with open(folder_name + '/' + file_name + '.xml', 'w') as f:
        f.write(ET.tostring(root, encoding='unicode'))

    remove_characters_between_xml_elements(root)
    with open(folder_name + '/' + file_name + '-compressed.xml', 'w') as f:
        f.write(ET.tostring(root, encoding='unicode'))

    json_object = xmltodict.parse(ET.tostring(root, encoding='utf-8'), force_list=('slot', 'type', 'attributes', 'element'))

    # write the json object to a file
    write_json_to_file(folder_name, file_name, json_object)


def write_attribute_names(root, folder_name, file_name, xpath):
    attribute_names = []
    for name in root.findall(xpath):
        # only append if not in attribute_names
        if name.text not in attribute_names:
            attribute_names.append(name.text)

    # sort the list of attribute names
    attribute_names.sort()

    with open(folder_name + '/' +  file_name + '.txt', 'w') as f:
        for item in attribute_names:
            f.write("%s\n" % item)


def remove_pages(root, parent_map, type_name_2_attribute_names):
    for page in root.findall('.//pages/page'):
        type_name = page.find('.//custom/type').text
        if type_name not in type_name_2_attribute_names:
            parent = parent_map[page]
            parent.remove(page)
        else:
            attribute_names = type_name_2_attribute_names[type_name]
            # if attribute_names has one element and this element is 'all'
            if len(attribute_names) == 0:
                pass
            else:
                custom = page.find('.//custom')
                attributes = custom.find('.//attributes')

                attributesToBeRemoved = []

                for attribute in attributes:
                    attribute_name = attribute.find('.//name').text
                    if attribute_name not in attribute_names:
                        # print("type " + type_name + " - removing attribute: " + attribute_name + " from page " + page.find('.//id').text)
                        # test if attribute is a child of attributes
                        # print(parent_map[attribute] == attributes)
                        attributesToBeRemoved.append(attribute)
                        # attributes.remove(attribute)
                        # print textual representation of page
                        # page_str = ET.tostring(page, encoding='utf-8', method='xml').decode('utf-8')
                        # print(page_str)

                for attribute in attributesToBeRemoved:
                    attributes.remove(attribute)

    remove(root, parent_map, './/pages/page/localizedName')
    remove(root, parent_map, './/pages/page/content')
    remove(root, parent_map, './/pages/page/tags')
    remove(root, parent_map, './/pages/page/orderable')
    remove(root, parent_map, './/pages/page/attachements')
    remove(root, parent_map, './/pages/page/widgetContainer')
    remove(root, parent_map, './/pages/page/pageInPackageInclusion')
    remove(root, parent_map, './/pages/page/layoutName')
    remove(root, parent_map, './/pages/page/nameGenerationCounter')


def rewrite_pages(root, parent_map):
    for attribute in root.findall('.//pages/page/custom/attributes/attribute'):
        attribute_name = attribute.find('.//name').text
        # set the attribute 'name' of the attribute element to the value of attribute_name
        attribute.set('name', attribute_name)
        # remove the name element
        attribute.remove(attribute.find('.//name'))
        values = attribute.find('.//values')
        for value in values:
            if value.text is not None:
                if value.text.startswith('s'):
                    # create a new element with the tag 'stringValue' and the text value.text
                    string_value = ET.Element('string')
                    string_value.set('value', value.text[1:])
                    attribute.append(string_value)
                    values.remove(value)
                elif value.text.startswith('d'):
                    number_value = ET.Element('number')
                    number_value.set('value', value.text[1:])
                    attribute.append(number_value)
                    values.remove(value)
                elif value.text.startswith('b'):
                    boolean_value = ET.Element('boolean')
                    boolean_value.set('value', value.text[1:])
                    attribute.append(boolean_value)
                    values.remove(value)
                elif value.text.startswith('l'):
                    reference_value = ET.Element('reference')
                    uid = value.text[1:]
                    # uid is of the form entityType/id - split the string at the first occurrence of '/'
                    entity_type, id = uid.split('/', 1)
                    # set the attribute 'entityType' of the referenceValue element to the value of entity_type
                    reference_value.set('entityType', entity_type)
                    # set the attribute 'id' of the referenceValue element to the value of id
                    reference_value.set('id', id)
                    attribute.append(reference_value)
                    values.remove(value)
                elif value.text.startswith('a'):
                    date_value = ET.Element('date')
                    date_value.set('value', value.text[1:])
                    attribute.append(date_value)
                    values.remove(value)
                elif value.text.startswith('r'):
                    rich_string_value = ET.Element('richString')
                    rich_string_value.text = value.text[1:]
                    attribute.append(rich_string_value)
                    values.remove(value)
                else:
                    print("unknown value type: " + value.text)
        attribute.remove(values)

    for attributes in root.findall('.//pages/page/custom/attributes'):
        custom = parent_map[attributes]
        # move all children of attributes to custom
        for attribute in list(attributes):
            custom.append(attribute)

        custom.remove(attributes)


def remove_all_pages(root):
    parent_map = get_parent_map(root)
    remove(root, parent_map, './/pages')


def remove_to_basics(root, parent_map):
    remove(root, parent_map, './/types/typeDef/localizedNamePlural')
    remove(root, parent_map, './/types/typeDef/iconName')
    remove(root, parent_map, './/types/typeDef/attributes/localizedShortName')
    remove(root, parent_map, './/types/typeDef/attributes/shortHelp')
    remove(root, parent_map, './/types/typeDef/attributes/multiplicity')
    remove(root, parent_map, './/types/typeDef/attributes/referenceConstraint/sameWorkspace')
    remove(root, parent_map, './/types/typeDef/attributes/referenceConstraint/isHierarchy')
    remove(root, parent_map, './/types/typeDef/attributes/textEnumerationConstraint/elements')
    remove(root, parent_map, './/types/typeDef/attributes/textEnumerationConstraint/element2icon')
    remove(root, parent_map, './/types/typeDef/attributes/textEnumerationConstraint/element2localizedLabel')
    remove(root, parent_map, './/types/typeDef/attributes/numberEnumerationConstraint/elements')
    remove(root, parent_map, './/types/typeDef/attributes/numberEnumerationConstraint/element2icon')
    remove(root, parent_map, './/types/typeDef/attributes/numberEnumerationConstraint/element2localizedLabel')
    remove(root, parent_map, './/types/typeDef/attributes/numberEnumerationConstraint/precision')
    remove(root, parent_map, './/types/typeDef/attributes/numberEnumerationConstraint/localizedTextAfterSupplier')
    remove(root, parent_map, './/types/typeDef/attributes/numberConstraint/precision')
    remove(root, parent_map, './/types/typeDef/attributes/numberConstraint/localizedTextAfterSupplier')
    remove(root, parent_map, './/types/typeDef/attributes/dateConstraint/specificity')
    remove(root, parent_map, './/types/typeDef/attributes/dateConstraint/dateFormat')
    remove(root, parent_map, './/types/typeDef/attributes/customConstraint')


def remove_generic_elements(root, parent_map):
    remove(root, parent_map, './/slot/shareable')
    remove(root, parent_map, './/package/shortname')

    remove(root, parent_map, './/workspace/pluginSpaceConfigurations')
    remove(root, parent_map, './/workspace/rootPage')
    remove(root, parent_map, './/workspace/lowCodeJobs')
    remove(root, parent_map, './/numberOfNonrootPages')
    remove(root, parent_map, './/workspace/customCssClasses')
    remove(root, parent_map, './/workspace/apps')
    remove(root, parent_map, './/workspace/id')
    remove(root, parent_map, './/workspace/numberOfNonrootPages')

    remove(root, parent_map, './/package/changelog')
    remove(root, parent_map, './/package/parentPackages')
    remove(root, parent_map, './/package/publishDate')
    remove(root, parent_map, './/package/cplaceRelease')
    remove(root, parent_map, './/package/description')

    remove(root, parent_map, './/maps')

    remove(root, parent_map, './/typeDef/nameTableColumnWidth')
    remove(root, parent_map, './/typeDef/defaultPageInPackageStrategy')
    remove(root, parent_map, './/typeDef/showInGlobalSearch')
    remove(root, parent_map, './/typeDef/localizedPageNamesMode')
    remove(root, parent_map, './/typeDef/appliesTo')
    remove(root, parent_map, './/typeDef/allowDivergentLayouts')
    remove(root, parent_map, './/typeDef/hideTabVersions')
    remove(root, parent_map, './/typeDef/showNewButton')
    remove(root, parent_map, './/typeDef/showInGlobalNewDialog')
    remove(root, parent_map, './/typeDef/enableIconLink')
    remove(root, parent_map, './/typeDef/namesAreUnique')
    remove(root, parent_map, './/typeDef/isTuple')
    remove(root, parent_map, './/typeDef/internalAttributeNamePrefix')
    remove(root, parent_map, './/typeDef/autocompleteDetailsPattern')
    remove(root, parent_map, './/typeDef/displayNameGenerationPattern')
    remove(root, parent_map, './/typeDef/nameGenerationPattern')
    # remove(root, parent_map, './/typeDef/iconName')
    remove(root, parent_map, './/typeDef/cplaceJSChangeListeners')
    remove(root, parent_map, './/typeDef/cplaceJSPageActions')


    remove(root, parent_map, './/typeDef/fixNameGenerationPattern')
    remove(root, parent_map, './/typeDef/fixDisplayNameGenerationPattern')
    remove(root, parent_map, './/typeDef/cplaceJSEditLanguageScript')
    remove(root, parent_map, './/typeDef/fixAutocompleteDetailsPattern')
    remove(root, parent_map, './/typeDef/showInExplorer')
    # remove(root, parent_map, './/typeDef/defaultWidgetContainerDef')
    # remove(root, parent_map, './/typeDef/name2additionalWidgetContainerDefs')
    remove(root, parent_map, './/typeDef/cplaceJSTypeMessages')
    remove(root, parent_map, './/typeDef/id')

    remove(root, parent_map, './/constraintFactory/fixedTypeNames')
    remove(root, parent_map, './/constraintFactory/showLinkAsTextOnly')
    remove(root, parent_map, './/constraintFactory/additionalFiltersSupplier')
    remove(root, parent_map, './/constraintFactory/additionalFilterValidationErrorMessage')
    remove(root, parent_map, './/constraintFactory/sortOrderForReference')
    remove(root, parent_map, './/constraintFactory/cplaceJSValidator')
    remove(root, parent_map, './/constraintFactory/readOnly')
    remove(root, parent_map, './/constraintFactory/isFixed')
    remove(root, parent_map, './/constraintFactory/queryableByApp')
    remove(root, parent_map, './/constraintFactory/queryableForScripting')
    remove(root, parent_map, './/constraintFactory/showMultiLine')
    remove(root, parent_map, './/constraintFactory/defaultValuesSupplier')
    remove(root, parent_map, './/constraintFactory/refreshAfterSetting')
    remove(root, parent_map, './/constraintFactory/validateAdditionalFilters')
    remove(root, parent_map, './/constraintFactory/showInverseRoleAsList')
    remove(root, parent_map, './/constraintFactory/showInMenuIfHierarchy')

    remove(root, parent_map, './/constraintFactory/regexp')
    remove(root, parent_map, './/constraintFactory/regexpErrorMessage')

    remove(root, parent_map, './/constraintFactory/dateFormatSupplier')
    remove(root, parent_map, './/constraintFactory/withTime')

    remove(root, parent_map, './/constraintFactory/attributeDefClass')
    remove(root, parent_map, './/constraintFactory/dynamicEnumerationProviderClass')

    remove(root, parent_map, './/typeDef/attributes/alternativeValueRepresentation')
    remove(root, parent_map, './/typeDef/attributes/cplaceJSValidator')
    remove(root, parent_map, './/typeDef/attributes/readOnly')
    remove(root, parent_map, './/typeDef/attributes/queryableForScripting')
    remove(root, parent_map, './/typeDef/attributes/queryableByApp')
    remove(root, parent_map, './/typeDef/attributes/showInColumnSelection')
    remove(root, parent_map, './/typeDef/attributes/tableColumnWidth')
    remove(root, parent_map, './/typeDef/attributes/showValuesWithLineBreak')
    remove(root, parent_map, './/typeDef/attributes/showInNewDialog')
    remove(root, parent_map, './/typeDef/attributes/showInAttributesWidget')
    remove(root, parent_map, './/typeDef/attributes/showInTables')
    remove(root, parent_map, './/typeDef/attributes/isFixed')

    remove(root, parent_map, './/typeDef/attributes/duplicatesAreAllowed')
    remove(root, parent_map, './/typeDef/attributes/showCreateNewButton')
    remove(root, parent_map, './/typeDef/attributes/derivedAttributeDef')

    attributes = root.findall('.//typeDef/attributes')
    for attribute in attributes:
        constraint_factory = attribute.find('.//constraintFactory')
        if constraint_factory.get('type') == 'dynamicEnumerationConstraint':
            parent_map[attribute].remove(attribute)


def rewrite_localized_name_attributes(doc):
    if isinstance(doc, list):
        for item in doc:
            rewrite_localized_name_attributes(item)
    elif isinstance(doc, dict):
        for key, value in doc.items():
            if key == 'localizedName' or key == 'localizedNameSingular' or key == 'localizedNamePlural' or key == 'localizedShortName':
                # parse the value as json and replace the value with the parsed json
                # print(json.loads(value))
                # print(value)
                if value is not None:
                    print(type(value) + " : " + value)
                    doc[key] = json.loads(value)

            rewrite_localized_name_attributes(value)


def rewrite_attributes(doc):
    if isinstance(doc, list):
        for item in doc:
            rewrite_attributes(item)
    elif isinstance(doc, dict):
        for key, value in doc.items():
            if value is not None and key == 'attributeDefinitions':
                # print (value)
                attribute_definition = value['attributeDefinition']
                # print(attributeDefinition)
                # print(type(attributeDefinition))
                # if attributeDefinition is a list, then create a new list

                new_list = []
                if isinstance(attribute_definition, list):
                    for attribute in attribute_definition:
                        new_list.append(attribute)

                    # replace the value with the list object
                    doc[key] = new_list

                elif isinstance(attribute_definition, dict):
                    new_list.append(attribute_definition)

                    # replace the value with the list object
                    doc[key] = new_list

            rewrite_attributes(value)

        # if the key is "enumerationValues" and the value is not None
        if 'enumerationValues' in doc and doc['enumerationValues'] is not None:
            # parse the value as json and replace the value with the parsed json
            new_value = json.loads(doc['enumerationValues'])
            # print the type of new_value
            if isinstance(new_value, list):
                # print the length of new_value
                # print(len(new_value))
                # iterate over all elements in new_value
                for i in range(len(new_value)):
                    value = new_value[i]
                    # if value is a string and starts with "s" - strip the first character and replace the value with the result
                    if isinstance(value, str) and value.startswith('s'):
                        new_value[i] = value[1:]
                    # if value is a string and starts with "d" - strip the first character, convert the value to a double and replace the value with the result
                    elif isinstance(value, str) and value.startswith('d'):
                        new_value[i] = float(value[1:])

            doc['enumerationValues'] = new_value

        # if the key is "enumerationValues2localizedLabels" and the value is not None
        if 'enumerationValues2localizedLabels' in doc and doc['enumerationValues2localizedLabels'] is not None:
            # parse the value as json and replace the value with the parsed json
            parsed_value = json.loads(doc['enumerationValues2localizedLabels'])

            if isinstance(parsed_value, dict):
                # q: how to prevent "RuntimeError: dictionary keys changed during iteration"?
                # a: create a new dictionary and iterate over the keys of the old dictionary

                new_value = {}

                for key, value in parsed_value.items():
                    if isinstance(key, str) and key.startswith('s'):
                        new_key = key[1:]
                        new_value[new_key] = parsed_value.get(key)
                    elif isinstance(key, str) and key.startswith('d'):
                        new_key = float(key[1:])
                        new_value[new_key] = parsed_value.get(key)

                doc['enumerationValues2localizedLabels'] = new_value


def rewrite_types(doc):
    # print("rewriteTypes: " + str(doc))
    if isinstance(doc, list):
        for item in doc:
            rewrite_types(item)
    elif isinstance(doc, dict):
        for key, value in doc.items():
            if value is not None and key == 'workspace':
                types = value['types']
                # print ("workspace: " + str(value))
                # print("type of types: " + str(type(value['types'])))

                type_ = types['type']
                # print("type of type: " + str(type(type_)))

                if isinstance(type_, list):
                    value['types'] = value['types']['type']
                else:
                    value['types'] = []
                    value['types'].append(type_)

            rewrite_types(value)
