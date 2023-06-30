import json
import os
import datetime
from commons.utils import create_folder

# ---------------------------------------------------------------------------------------------------------------------#
#                    Functions to manipulate JSON files information and responses                                      #
# ---------------------------------------------------------------------------------------------------------------------#

# ------------------------------------------------- JSON Functions ----------------------------------------------------#


def load_json_as_string(json_file_path):
    json_file = json_file_path
    with open(json_file, 'r') as file:
        json_data = json.loads(file)
        return json_data


def load_json_as_dict(json_file_path):
    json_file = json_file_path
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        return json_data


def read_scenario_from_json(scenario, key, json_file_path):
    json_file = json_file_path
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        if json_data.get(scenario).get(key):
            return json_data.get(scenario).get(key)
        return None


def get_json_keys(json_file_path):
    json_file = load_json_as_dict(json_file_path)
    return json_file.keys()


def get_json_values(json_file_path):
    json_file = load_json_as_dict(json_file_path)
    return json_file.values()


def write_json_file(json_object, request_name):
    folder_path = os.path.join(os.getcwd(), "json_generated")
    date_time = str(datetime.date.today())
    create_folder(folder_path)
    create_folder(folder_path + "/" + date_time)
    file_path = os.path.join(os.getcwd(), folder_path + "/" + date_time, request_name + ".json")

    with open(file_path, "w") as outfile:
            json.dump(json_object.replace('"[', '[').replace(']"', ']').replace(
            '"{ ', '{').replace('}"', '}').replace(' ', '').replace('\n', '').replace('\"','"'), outfile,  indent=1, ensure_ascii=False)


def beautify_json(json_template_name, json_string):
    try:
        return json.dumps(json.loads(json_string), indent=4, ensure_ascii=False).encode('utf8')
    except json.decoder.JSONDecodeError as err:  # includes simplejson.decoder.JSONDecodeError
        body = json_string.replace('"[', '[').replace(']"', ']').replace(
            '"{ ', '{').replace('}"', '}').replace(' ', '').replace('\n', '')
        error_message = "JSON error decoding file: '{0}'".format(err)
        message = "Check if the template " + json_template_name + " is malformed. " \
                                                                  "Check the body request, fix your template file" \
                                                                  " and try again." \
                                                                  "\nError Message: " + error_message + \
                  "\nBODY REQUEST: " + body

        raise Exception(message)


def find_key_and_replace_value_json(obj, key, value):
    if key in obj:
        obj[key] = value
        return obj[key]
    if type(obj) is str:
        json.dumps(obj, indent=2, sort_keys=True)
    if type(obj) is dict:
        for k, v in obj.items():
            if isinstance(v, dict):
                item = find_key_and_replace_value_json(v, key, value)
                if item is not None:
                    return json.dumps(obj, indent=2, sort_keys=True)
    elif type(obj) is list:
        for k, v in enumerate(obj):
            item = find_key_and_replace_value_json(v, key, value)
            if item is not None:
                return json.dumps(obj, indent=2, sort_keys=True)


def add_if_key_not_exist(dict_obj, key, value):
    """ Add new key-value pair to dictionary only if
    key does not exist in dictionary. """
    result = dict()
    if key not in dict_obj:
        result.update({key: value})


def convert_to_dict(data):
    converted_data = None
    if type(data) is list:
        for index, item in enumerate(data):
            # Convert to dict
            converted_data = eval(data[index])
            # Load json file
    elif type(data) is dict:
        converted_data = data
    else:
        print("\nType is different from 'list' or 'dict'")
    return converted_data


def edit_json(json_data, args):
    new_json = []
    for args_key, args_value in args.items():
        for key, value in json_data.items():
            if args_key == key and args_value != value:
                json_data[key] = args_value
            else:
                new_json_data = json_data[key]
                if (type(new_json_data) is dict) or (type(new_json_data) is list):
                    item = find_key_and_replace_value_json(new_json_data, args_key, args_value)
                    if (item is not None) or (type(item) is str):
                        json.dumps(json_data, indent=2, sort_keys=True)
    new_json.append(json_data)
    return new_json


def edit_template_json(json_file_path, args_data):
    new_json = []
    json_file = json_file_path
    if type(args_data) is list:
        for index, item in enumerate(args_data):
            # Convert to dict
            args = eval(args_data[index])
            # Load json file
            with open(json_file, 'r') as file:
                data = json.load(file)
                # If .json starts with "[", Python will load as a list, so you need to convert it for to dict
                json_data = convert_to_dict(data)
                new_json_data = edit_json(json_data, args)
                new_json.append(json.dumps(new_json_data, sort_keys=True))
    if type(args_data) is dict:
        args = args_data
        with open(json_file, 'r') as file:
            data = json.load(file)
            # If .json starts with "[", Python will load as a list, so you need to convert it for to dict
            json_data = convert_to_dict(data)
            new_json = edit_json(json_data, args)
            new_json.append(json.dumps(new_json_data, sort_keys=True))
    return new_json

