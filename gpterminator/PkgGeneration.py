import json
import os

from dicttoxml import dicttoxml
import xml.etree.ElementTree as ET

from gpterminator.Utils import get_parent_map, pretty_print_xml, remove_tags


def generatePackage(application_name, pkg_version):
    types_detailed_file_name = 'applications/' + application_name + '/types-detailed.json'
    with open(types_detailed_file_name, 'r') as file:
        types_detailed = json.load(file)

    types_rewritten = {
        'types': []
    }

    for type_ in types_detailed:
        types_rewritten['types'].append({
            'typeDef': type_
        })

        type_name = type_['internalName']
        type_['name'] = type_name
        del type_['internalName']
        type_['appliesTo'] = {
            'key': 'page'
        }
        type_['localizedPageNamesMode'] = {
            'key': 'none'
        }

        new_attributes = []
        for attribute in type_['attributes']:
            new_attributes.append({
                'attributes': attribute
            })

            multiplicity = attribute['multiplicity']
            del attribute['multiplicity']

            internal_name = attribute['internalName']
            attribute['name'] = internal_name
            del attribute['internalName']

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
            elif 'longText' == attribute_type:
                constraint_factory_type = 'longConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')
            elif 'textEnumeration' == attribute_type:
                constraint_factory_type = 'textEnumerationConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleStringAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiStringAttributeDef')
            elif 'numberEnumeration' == attribute_type:
                constraint_factory_type = 'numberEnumerationConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleNumberAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiNumberAttributeDef')
            elif 'reference' == attribute_type:
                constraint_factory_type = 'referenceConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleReferenceAttributeDef$SingleCustomReferenceAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiReferenceAttributeDef$MultiCustomReferenceAttributeDef')
            elif 'date' == attribute_type:
                constraint_factory_type = 'dateConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleDateAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiDateAttributeDef')
            elif 'number' == attribute_type:
                constraint_factory_type = 'numberConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleNumberAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiNumberAttributeDef')
            elif 'boolean' == attribute_type:
                constraint_factory_type = 'booleanConstraint'
                attribute_def_class = getAttributeDefClass(multiplicity, 'cf.cplace.platform.assets.custom.def.SingleBooleanAttributeDef', 'cf.cplace.platform.assets.custom.def.MultiBooleanAttributeDef')
            elif 'richString' == attribute_type:
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
            "version": pkg_version,
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
                        "apps": "[\"cf.cplace.platform\"]",
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

    # with open('applications/' + application_name + '/types-detailed-rewritten.json', 'w') as file:
    #     json.dump(new_root, file, indent=4)

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
    with open('applications/' + application_name + '/generated/export.xml', 'w') as file:
        file.write(xml_str)

    # zip export.xml into package.zip
    os.system("zip -j " + 'applications/' + application_name + "/generated/package.zip " + 'applications/' + application_name + "/generated/export.xml")


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
