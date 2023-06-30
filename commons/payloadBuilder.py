import os
import json
import jinja2
from commons.csvDataBuilder import select_csv_strategy
from commons.stringManipulation import split_string_after
from environment import get_execute_flag, get_data_param_keys


# ---------------------------------------------------------------------------------------------------------------------#
#                                        Functions to build body requests                                              #
# ---------------------------------------------------------------------------------------------------------------------#

# ----------------------------------------- Payload Builder Functions -------------------------------------------------#


def create_generic_relay_payload_body(json_template_name, edited_json, service, version):
    if not get_execute_flag():
        payload = get_beautified_payload(json_template_name, edited_json).decode('utf8')
    else:
        payload = str(json.dumps(edited_json.replace('\n', '')))
    template = get_template_from_folder(os.path.join(os.getcwd(), "templates/bodies"), "middleware.json")
    payload_data = {
        "service": service.upper(),
        "version": version,
        "payload": payload
    }
    return template.render(payload_data)


def create_generic_relay_payload(json_template_name, data, multiple_request, service, version):
    edited_json = template_editor(json_template_name, data, multiple_request)
    if multiple_request:
        return [create_generic_relay_payload_body(json_template_name, data, service, version) for data
                in edited_json]
    return create_generic_relay_payload_body(json_template_name, edited_json, service, version)


def create_standard_payload(template_name, data, multiple_request):
    edited_json = template_editor(template_name, data, multiple_request)
    body = get_beautified_payload(template_name, edited_json)
    return body


def create_payload(template_name, data, service, method, version, multiple_request=False, request_through_middleware_api=False):
    if request_through_middleware_api:
        payload = create_generic_relay_payload(template_name, data, multiple_request, service, version)
    elif not request_through_middleware_api and method == "get":
        payload = data
    else:
        payload = create_standard_payload(template_name, data, multiple_request)
    return payload


def get_template_from_folder(folder_path, template_name):
    file_folder = jinja2.FileSystemLoader(searchpath=folder_path)
    template_env = jinja2.Environment(loader=file_folder)
    template = template_env.get_template(template_name)
    return template


def template_editor(json_template_name, data, multiple_request):
    if json_template_name != "None" and json_template_name != "none" and json_template_name is not None and data is not None:
        json_template = json_template_name + ".json"
        template = get_template_from_folder(os.path.join(os.getcwd(), "templates"), json_template)
        if multiple_request and type(data) is list:
            return [template.render(dict_list=[d]) for d in data]
        else:
            return template.render(dict_list=data)
    else:
        return data


def data_and_header_creation(strategy=None, data_source=None, country=None,  prefix=None,  scenario=None, data_flow=None, param_keys=None, static_params=None, amount_data_mass=None):
    data = []
    header = []
    count = 1
    if data_source is None and data_flow is None and param_keys is None:
        raise ValueError(f""" 
            Something goes wrong. Check in your yaml configuration!
            data_source and data_flow and param_keys can't be None at the same time
        """)
    if not data_source or data_source == 'None' or data_source == 'none':
        while count <= amount_data_mass:
            # Convert to dict
            param_keys = get_data_param_keys(country, param_keys, static_params, prefix)
            if param_keys != 'None' and param_keys != 'none' and param_keys != '' and param_keys is not None:
                header.append({key: value for key, value in param_keys.items() if key.startswith('header_')})
                data.append({key: value for key, value in param_keys.items() if not key.startswith('header_')})
            elif param_keys is None and data_flow is not None:
                for index, item in enumerate(data_flow):
                    data_flow_line = data_flow[index]
                    header.append({split_string_after(key, 'header_'): value for key, value in data_flow_line.items() if
                                   key.startswith('header_')})
                    data.append({key: value for key, value in data_flow_line.items() if not key.startswith('header_')})
            else:
                return "You need to inform or parameters in param_keys in the config.yml or select a FLOW define in config_flow.yml"
            count = count + 1
        return data, header
    else:
        csv_data = select_csv_strategy(country, data_source, strategy, scenario, param_keys, static_params, prefix)
        for index, item in enumerate(csv_data):
            # Convert to dict
            csv_line = eval(csv_data[index])
            header.append({split_string_after(key, 'header_'): value for key, value in csv_line.items() if
                           key.startswith('header_')})
            data.append({key: value for key, value in csv_line.items() if not key.startswith('header_')})
        return data, header


def get_beautified_payload(json_template_name, payload):
    body_list = []
    if type(payload) is not list:
        body = payload.replace('\n', '').replace('"[', '[').replace(']"', ']').replace(
            '"{ ', '{').replace('}"', '}')
        if type(payload) is dict:
            body = json.dumps(payload)
        return beautify_json(json_template_name, body)
    else:
        for body in payload:
            if type(body) is dict:
                body_list.append(beautify_json(json_template_name, json.dumps(body)))
            else:
                body_list.append(beautify_json(json_template_name, body))
        return body_list


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
