import json


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


def get_json_keys(json_file_path):
    json_file = load_json_as_dict(json_file_path)
    return json_file.keys()


def get_json_values(json_file_path):
    json_file = load_json_as_dict(json_file_path)
    return json_file.values()


def write_json_file(json_string):
    new_json = json.dumps(json_string, sort_keys=True)
    open("new_json.json", "w").write(new_json)


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
