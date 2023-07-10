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


