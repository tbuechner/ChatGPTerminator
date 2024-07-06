import json
import os
import string
import xml
import random

from xml.dom import minidom

import xml.etree.ElementTree as ET
import xmltodict

from gpterminator.ProcessPackageUtil import write_json_to_file

def transform_value(value):
    # if value has key string
    if 'string' in value:
        return value['string']
    elif 'richStringValue' in value:
        return value['richStringValue']
    elif 'numberValue' in value:
        return float(value['numberValue'])
    elif 'boolean' in value:
        # return a boolean
        return bool(value['boolean'])
    elif 'localizedString' in value:
        return json.loads(value['localizedString'])
    else:
        print("No value found: ", value)
        return None


def add_widgets(each, parent_map, widgetId2widget, result):
    for content in each.findall('.//content'):
        widget_id = content.find('id').text
        configuration_text = content.find('configuration').text
        if configuration_text is None:
            configuration_text = '{}'
        configuration = json.loads(configuration_text)

        for each_configuration in configuration:
            values = each_configuration['values']
            new_values = []
            for value in values:
                new_value = transform_value(value)
                new_values.append(new_value)

            if len(new_values) == 1:
                new_values = new_values[0]
            each_configuration['value'] = new_values
            del each_configuration['values']


        widget_type = content.find('widgetType').text
        widget = {
            'id': widget_id,
            'attributes': configuration,
            'widgetType': widget_type,
        }

        widgetId2widget[widget_id] = widget

    rows_array = []
    widget = {
        'layoutType': 'typeLayout',
        'rows': rows_array
    }
    result.append(widget)
    for layout in each.findall('.//layout'):
        for row in layout.findall('.//rows'):
            column_array = []
            row_object = {
                'columns': column_array,
            }
            rows_array.append(row_object)
            for column in row.findall('.//columns'):
                proportion = column.find('proportion').text
                proportion = int(proportion)
                widgets_array = []
                column_object = {
                    'proportion': proportion,
                    'widgets': widgets_array,
                }
                column_array.append(column_object)
                for widget in column.findall('widgets'):
                    widget_id = widget.find('id').text
                    widget = widgetId2widget[widget_id]
                    widgets_array.append(widget)


def find_all_widgets(root, parent_map):

    result = []

    widgetId2widget = {}

    for each in root.findall('.//defaultWidgetContainerDef'):
        add_widgets(each, parent_map, widgetId2widget, result)

    for each in root.findall('.//name2additionalWidgetContainerDefs'):
        for each_each in each.findall('.//entry'):
            add_widgets(each_each.find('value'), parent_map, widgetId2widget, result)


    # Find elements by XPath and remove them
    for target in root.findall('.//widgetContainer'):

        parent = parent_map[target]

        # convert target from xml to json
        as_json = xmltodict.parse(ET.tostring(target, encoding='utf-8', method='xml').decode('utf-8'))

        # print(asJson)

        widget_container = as_json['widgetContainer']

        # parse widgetsLayout value of widgetContainer as json
        # print(widgetContainer['widgetsLayout'])

        widget_id2widget = {}

        layout_ = widget_container['widgetsLayout']
        if layout_ is not None:
            layout_as_json = json.loads(layout_)
            widget_container['widgetsLayout'] = layout_as_json

            widgets = widget_container['widgets']
            if widgets is not None:
                actual_widgets = widgets['widget']
                if actual_widgets is not None:
                    if isinstance(actual_widgets, list):
                        for widget in actual_widgets:
                            widget_id = widget['widgetId']
                            widget_id2widget[widget_id] = widget
                            # print ("adding: ", widgetId, widget)
                    elif isinstance(actual_widgets, dict):
                        widget_id = actual_widgets['widgetId']
                        widget_id2widget[widget_id] = actual_widgets
                        # print ("is dict")
                        # print (actualWidgets)
                    # else:
                    #     # print type of actualWidgets
                    #     # print("No list nor dict" + str(type(actualWidgets)))
                # else:
                #     # print("No widgets found - 2")
            # else:
            #     print("No widgets found - 1")

            for row in layout_as_json['rows']:
                for column in row['columns']:
                    for widget in column['widgets']:
                        widget_id = widget['id']
                        # print(widgetId)
                        # print("widgetId2widget: " + str(widgetId2widget))

                        # test if the widgetId is in the map widgetId2widget
                        if widget_id in widget_id2widget:
                            widget_from_map = widget_id2widget[widget_id]

                            # iterate over the keys of the widgetFromMap
                            for key in widget_from_map:
                                # if the key is not in the widget, then add it
                                if key not in widget:
                                    value = widget_from_map[key]
                                    if key == 'attributes' and value is not None:
                                        # print ("value: ", json.dumps(value, separators=(',', ':')))
                                        new_value = value['attribute']
                                        if isinstance(new_value, list):
                                            for eachValue in new_value:
                                                # print(eachValue['values'])
                                                eachValue['value'] = eachValue['values']['value']
                                                del eachValue['values']
                                                if 'embeddedWidgets_values' in eachValue:
                                                    del eachValue['embeddedWidgets_values']
                                        else:
                                            new_value['value'] = new_value['values']['value']
                                            del new_value['values']
                                            if 'embeddedWidgets_values' in new_value:
                                                del new_value['embeddedWidgets_values']

                                        widget[key] = new_value
                                    else:
                                        widget[key] = value

                            del widget['widgetId']
                        else:
                            print("Widget not found: ", widget_id, widget_id2widget)

            # print(json.dumps(layoutAsJson, separators=(',', ':')))
            result.append(layout_as_json)

            layout_type = parent.tag
            if 'page' == layout_type:
                layout_type = 'pageLayout'
            elif 'type' == layout_type:
                layout_type = 'typeLayout'

            layout_as_json['layoutType'] = layout_type

            if 'typeDefinitionLayout' == parent.tag:
                as_json = xmltodict.parse(ET.tostring(parent, encoding='utf-8', method='xml').decode('utf-8'))
                type_definition_layout = as_json['typeDefinitionLayout']
                layout_as_json['internalLayoutName'] = type_definition_layout['internalName']
                layout_as_json['localizedLayoutName'] = json.loads(type_definition_layout['localizedName'])

                type_ = parent_map[parent_map[parent]]
                as_json = xmltodict.parse(ET.tostring(type_, encoding='utf-8', method='xml').decode('utf-8'))
                layout_as_json['typeName'] = as_json['type']['name']

        if 'type' == parent.tag:
            as_json = xmltodict.parse(ET.tostring(parent, encoding='utf-8', method='xml').decode('utf-8'))
            type_definition_layout = as_json['type']
            layout_as_json['typeName'] = type_definition_layout['name']

    return result


def rewrite_widgets(widgets):
    # iterate over all widgets
    for widget in widgets:
        # iterate over all rows
        for row in widget['rows']:
            # iterate over all columns
            for column in row['columns']:
                # iterate over all widgets
                for widget_ in column['widgets']:
                    # remove 'collapsed' key from widget_
                    if 'collapsed' in widget_:
                        del widget_['collapsed']
                    # remove 'id' key from widget_
                    if 'id' in widget_:
                        del widget_['id']
                    if 'attributes' in widget_:
                        attributes = widget_['attributes']
                        if isinstance(attributes, list):
                            for attribute in attributes:
                                if 'value' in attribute:
                                    value = attribute['value']
                                    # if value is a string and starts with "s" - strip the first character and replace the value with the result
                                    if isinstance(value, str) and (value.startswith('s') or value.startswith('m')):
                                        new_value = value[1:]
                                        # test if new_value is a json string or json array
                                        if new_value.startswith('{') or new_value.startswith('['):
                                            # parse new_value as json - catch json.decoder.JSONDecodeError
                                            try:
                                                new_value = json.loads(new_value)
                                            except json.decoder.JSONDecodeError:
                                                print("Error parsing json: ", new_value)

                                            # if new_value is a dictionary and has a key "widgets" and "widgetsLayout"
                                            if isinstance(new_value, dict) and 'widgets' in new_value and 'widgetsLayout' in new_value:

                                                widget_id_2_widget = {}

                                                widgets = json.loads(new_value['widgets'])
                                                # iterate over all widgets
                                                for widget__ in widgets:
                                                    # if the widget has a key "configuration"
                                                    if 'configuration' in widget__:
                                                        # convert configuration value of widget to json
                                                        widget__['configuration'] = json.loads(widget__['configuration'])
                                                    # if the widget has a key "id"
                                                    widget_id_2_widget[widget__['id']] = widget__

                                                del new_value['widgets']
                                                # new_value['widgets'] = widgets

                                                # convert widgetsLayout value of new_value to json
                                                widgets_layout = json.loads(new_value['widgetsLayout'])
                                                new_value['widgetsLayout'] = widgets_layout

                                                # iterate over all rows
                                                for row_ in widgets_layout['rows']:
                                                    # iterate over all columns
                                                    for column_ in row_['columns']:
                                                        # iterate over all widgets
                                                        new_widgets = []
                                                        for widget__ in column_['widgets']:
                                                            widget_id = widget__['id']
                                                            # test if the widgetId is in the map widgetId2widget
                                                            if widget_id in widget_id_2_widget:
                                                                widget_from_map = widget_id_2_widget[widget_id]
                                                                del widget_from_map['id']

                                                                new_widgets.append(widget_from_map)

                                                                del widget__['id']
                                                            else:
                                                                print("Widget not found: ", widget_id, widget_id_2_widget)

                                                        column_['widgets'] = new_widgets


                                        attribute['value'] = new_value
                                    # if value is a string and starts with "b" - strip the first character and convert the value to a boolean
                                    elif isinstance(value, str) and value.startswith('b'):
                                        attribute['value'] = value[1:] == 'true'
                                    # if value is a string and starts with "d" - strip the first character and convert the value to a number
                                    elif isinstance(value, str) and value.startswith('d'):
                                        attribute['value'] = float(value[1:])
                                    elif isinstance(value, str) and value.startswith('r'):
                                        attribute['value'] = value[1:]


def rewrite_widgets(widgets):
    # iterate over all widgets
    for widget in widgets:
        # iterate over all rows
        for row in widget['rows']:
            # iterate over all columns
            for column in row['columns']:
                # iterate over all widgets
                for widget_ in column['widgets']:
                    # remove 'collapsed' key from widget_
                    if 'collapsed' in widget_:
                        del widget_['collapsed']
                    # remove 'id' key from widget_
                    if 'id' in widget_:
                        del widget_['id']
                    if 'attributes' in widget_:
                        attributes = widget_['attributes']
                        if isinstance(attributes, list):
                            for attribute in attributes:
                                if 'value' in attribute:
                                    value = attribute['value']
                                    # if value is a string and starts with "s" - strip the first character and replace the value with the result
                                    if isinstance(value, str) and (value.startswith('s') or value.startswith('m')):
                                        new_value = value[1:]
                                        # test if new_value is a json string or json array
                                        if new_value.startswith('{') or new_value.startswith('['):
                                            # parse new_value as json - catch json.decoder.JSONDecodeError
                                            try:
                                                new_value = json.loads(new_value)
                                            except json.decoder.JSONDecodeError:
                                                print("Error parsing json: ", new_value)

                                            # if new_value is a dictionary and has a key "widgets" and "widgetsLayout"
                                            if isinstance(new_value, dict) and 'widgets' in new_value and 'widgetsLayout' in new_value:

                                                widget_id_2_widget = {}

                                                widgets = json.loads(new_value['widgets'])
                                                # iterate over all widgets
                                                for widget__ in widgets:
                                                    # if the widget has a key "configuration"
                                                    if 'configuration' in widget__:
                                                        # convert configuration value of widget to json
                                                        widget__['configuration'] = json.loads(widget__['configuration'])
                                                    # if the widget has a key "id"
                                                    widget_id_2_widget[widget__['id']] = widget__

                                                del new_value['widgets']
                                                # new_value['widgets'] = widgets

                                                # convert widgetsLayout value of new_value to json
                                                widgets_layout = json.loads(new_value['widgetsLayout'])
                                                new_value['widgetsLayout'] = widgets_layout

                                                # iterate over all rows
                                                for row_ in widgets_layout['rows']:
                                                    # iterate over all columns
                                                    for column_ in row_['columns']:
                                                        # iterate over all widgets
                                                        new_widgets = []
                                                        for widget__ in column_['widgets']:
                                                            widget_id = widget__['id']
                                                            # test if the widgetId is in the map widgetId2widget
                                                            if widget_id in widget_id_2_widget:
                                                                widget_from_map = widget_id_2_widget[widget_id]
                                                                del widget_from_map['id']

                                                                new_widgets.append(widget_from_map)

                                                                del widget__['id']
                                                            else:
                                                                print("Widget not found: ", widget_id, widget_id_2_widget)

                                                        column_['widgets'] = new_widgets


                                        attribute['value'] = new_value
                                    # if value is a string and starts with "b" - strip the first character and convert the value to a boolean
                                    elif isinstance(value, str) and value.startswith('b'):
                                        attribute['value'] = value[1:] == 'true'
                                    # if value is a string and starts with "d" - strip the first character and convert the value to a number
                                    elif isinstance(value, str) and value.startswith('d'):
                                        attribute['value'] = float(value[1:])
                                    elif isinstance(value, str) and value.startswith('r'):
                                        attribute['value'] = value[1:]



def count_widget_kinds(widgets, folder_name_generated):
    widget_kind_2_count = {}

    # iterate over all widgets
    for widget in widgets:
        # iterate over all rows
        for row in widget['rows']:
            # iterate over all columns
            for column in row['columns']:
                # iterate over all widgets
                for widget_ in column['widgets']:
                    widget_type = widget_['widgetType']

                    # increase the count of the widgetType by 1
                    if widget_type in widget_kind_2_count:
                        widget_kind_2_count[widget_type] += 1
                    else:
                        widget_kind_2_count[widget_type] = 1

    with open(folder_name_generated + '/' + 'widget-kind-to-count.json', 'w') as f:
        f.write(json.dumps(widget_kind_2_count, indent=4))



def condense_widgets(widgets):

    # iterate over all widgets
    for widget in widgets:
        # iterate over all rows
        for row in widget['rows']:
            # iterate over all columns
            for column in row['columns']:
                # iterate over all widgets
                for widget_ in column['widgets']:
                    strip_embedded_widgets(widget_)

                    widget_type = widget_['widgetType']

                    # if widget_type equals 'cf.cplace.visualizations.scriptingHighcharts'
                    if widget_type == 'cf.cplace.visualizations.scriptingHighcharts':
                        remove_attribute(widget_, 'cf.cplace.visualization.script')
                        remove_attribute(widget_, 'cf.cplace.visualization.showFrame')
                        remove_attribute(widget_, 'height')
                        remove_attribute(widget_, 'sortOrder')

                    if widget_type == 'de.visualistik.visualRoadmap.widget':
                        remove_all_attributes(widget_)

                    if widget_type == 'cf.cplace.platform.connectedAttributesGroup':
                        remove_attribute(widget_, 'singleSelectionWidgetId')
                        remove_attribute(widget_, 'singleColumn')
                        remove_attribute(widget_, 'height')
                        remove_attribute(widget_, 'cf.cplace.platform.useNewFrontend')
                        remove_attribute(widget_, 'cf.cplace.platform.attributesGroup.showFrame')
                        condense_attributes_group(get_attribute_value(widget_, 'cf.cplace.platform.attributesGroup.layout'))

                    if widget_type == 'cf.cplace.platform.attributesGroup':
                        remove_attribute(widget_, 'cf.cplace.platform.attributesGroup.showFrame')
                        remove_attribute(widget_, 'cf.cplace.platform.attributesGroup.useNewFrontend')
                        remove_attribute(widget_, 'cf.platform.attributesGroup.enableMultiEdit')
                        remove_attribute(widget_, 'cf.platform.singleColumn')
                        condense_attributes_group(get_attribute_value(widget_, 'cf.cplace.platform.attributesGroup.layout'))

                    if widget_type == 'cf.platform.embeddedSearchAsTable':
                        remove_attribute(widget_, 'showTableActions')
                        remove_attribute(widget_, 'showTableFooter')
                        remove_attribute(widget_, 'showTableHeader')
                        remove_attribute(widget_, 'singleSpaced')
                        remove_attribute(widget_, 'showNewButton')
                        remove_attribute(widget_, 'hideTableLinks')
                        remove_attribute(widget_, 'hideNames')
                        remove_attribute(widget_, 'height')
                        remove_attribute(widget_, 'groupOrder')
                        remove_attribute(widget_, 'columns')
                        rewrite_search(get_attribute_value(widget_, 'search'))

                    if 'attributes' in widget_ and widget_['attributes'] is None:
                        del widget_['attributes']


def strip_embedded_widgets(widget_):
    if 'attributes' in widget_:
        if isinstance(widget_['attributes'], list):
            for attribute in widget_['attributes']:
                replace_embedded_widget_in_attribute(attribute)
        elif isinstance(widget_['attributes'], dict):
            replace_embedded_widget_in_attribute(widget_['attributes'])
    else:
        print("No attributes found: ", widget_)



def replace_embedded_widget_in_attribute(attribute):
    if isinstance(attribute, dict) and 'value' in attribute and attribute['value'] is not None:
        value = attribute['value']
        if isinstance(value, str):
            # if value contains <embeddedwidget>any_content</embeddedwidget> at any place - strip the content between the tags
            attribute['value'] = replace_embedded_widget(value)


def replace_embedded_widget(value):

    while '<embeddedwidget>' in value:
        # find the index of '<embeddedwidget>'
        start = value.find('<embeddedwidget>')
        # find the index of '</embeddedwidget>'
        end = value.find('</embeddedwidget>')
        # replace the content between '<embeddedwidget>' and '</embeddedwidget>' with '<_embeddedwidget_>'
        value = value[:start] + '<_embeddedwidget_>' + value[end + len('</embeddedwidget>'):]
        # print("value: ", value)

    return value


def remove_attribute(widget_, name):
    if 'attributes' in widget_:
        for attribute in widget_['attributes']:
            if 'name' in attribute and attribute['name'] == name:
                # remove the attribute
                widget_['attributes'].remove(attribute)


def remove_all_attributes(widget_):
    del widget_['attributes']


def condense_attributes_group(value):
    layout = json.loads(value['widgetsLayout'])
    for row in layout['rows']:
        # iterate over all columns
        for column in row['columns']:
            # iterate over all widgets
            for widget_ in column['widgets']:
                remove_configuration(widget_, 'cf.platform.inPlaceEditing')
                remove_configuration(widget_, 'cf.platform.reloadAfterChange')
                remove_configuration(widget_, 'cf.platform.useParent')
                remove_configuration(widget_, 'cf.platform.singleColumn')
                remove_configuration(widget_, 'cf.platform.withLabel')
                remove_configuration(widget_, 'cf.platform.withValue')

                remove_configuration(widget_, 'inPlaceEditing')
                remove_configuration(widget_, 'reloadAfterChange')
                remove_configuration(widget_, 'showAttributeScript')
                remove_configuration(widget_, 'singleColumn')
                remove_configuration(widget_, 'singleSelectionWidgetId')
                remove_configuration(widget_, 'withLabel')
                remove_configuration(widget_, 'withValue')


def remove_configuration(widget_, name):
    if 'configuration' in widget_:
        for attribute in widget_['configuration']:
            if 'name' in attribute and attribute['name'] == name:
                # remove the attribute
                widget_['configuration'].remove(attribute)


def get_attribute_value(widget_, name):
    if 'attributes' in widget_:
        for attribute in widget_['attributes']:
            if 'name' in attribute and attribute['name'] == name:
                return json.loads(attribute['value'])


def rewrite_search(search):
    for filter in search['filters']:
        if 'customAttributeMultiExactValues' in filter:
            for value in filter['values']:
                if isinstance(value, str) and value.startswith('s'):
                    # replace the value in the list with the result of stripping the first character
                    filter['values'][filter['values'].index(value)] = value[1:]
                elif isinstance(value, str) and value.startswith('d'):
                    filter['values'][filter['values'].index(value)] = float(value[1:])


def write_widgets_per_type(widgets, widgets_for_types_folder, folder_name_generated):
    type_2_widgets = {}
    type_2_count = {}

    for widget in widgets:
        layout_type = widget['layoutType']
        if 'typeDefinitionLayout' == layout_type:

            type_name = widget['typeName']
            if type_name is not None:
                if type_name in type_2_widgets:
                    type_2_widgets[type_name].append(widget)
                else:
                    type_2_widgets[type_name] = [widget]

                # increase the count by 1
                if type_name in type_2_count:
                    type_2_count[type_name] += 1
                else:
                    type_2_count[type_name] = 1

    for type_name in type_2_widgets:

        simple_type_name = type_name.split(".")[-1]
        simple_type_name = simple_type_name[0].lower() + simple_type_name[1:]

        widgets = type_2_widgets[type_name]

        write_json_to_file(widgets_for_types_folder, simple_type_name + '-widgets', widgets, True)


    with open(folder_name_generated + '/' + 'widget-type-to-count.json', 'w') as f:
        f.write(json.dumps(type_2_count, indent=4))
