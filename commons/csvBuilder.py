import json
import csv
import pandas as pd
import environment
import os.path
import os

from commons.stringManipulation import split_string_after
from environment import get_csv_strategy, get_csv_scenario, get_config_from_version


# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate CSV data files                                         #
# ---------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------- CSV Functions ----------------------------------------------------#


def write_responses_in_csv(response, data_unique_id, request_name, multiple_request, request_through_middlewre_api):
    file_path = os.path.join(os.getcwd(), "request_results", "output_data-"+request_name+".csv")
    if not multiple_request:
        delete_output_file(file_path)
    header = set()
    # receiving results in a dictionary
    response_dict = json.loads(response)
    if request_through_middlewre_api:
        payload_list = json.loads(response_dict["payload"])
    else:
        payload_list = json.loads(json.dumps(response_dict))
    if type(payload_list) is dict:
        payload_list["data_unique_id"] = data_unique_id
        for key in payload_list.keys():
            header.add(key)
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for payload in payload_list:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([payload_list[key] if key in payload else "" for key in header])
    else:
        for payload in payload_list:
            payload["data_unique_id"] = data_unique_id
            for key in payload.keys():
                header.add(key)
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for payload in payload_list:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([payload[key] if key in payload else "" for key in header])


def delete_output_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def load_csv(csv_file_path):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def load_csv_and_param_keys(csv_file_path, country, service, method, version):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            param_keys = environment.get_param_keys(country, service, method, version)
            row.update(param_keys)
            new_json.append((json.dumps(row, sort_keys=True)))
    return new_json


def load_csv_multiple_lines(csv_file, group_key, output_list_name, list_fields):
    result = {}
    with open(csv_file, 'r') as fh:
        csv_reader = csv.DictReader(fh)
        for row in csv_reader:
            group_key_joined = get_group_key(row, group_key)
            if group_key_joined not in result:
                result[group_key_joined] = row.copy()
                result[group_key_joined][output_list_name] = []
            result[group_key_joined][output_list_name].append({field: row[field] for field in list_fields})

    return [json.dumps(data) for data in result.values()]


def get_group_key(row, group_key):
    return "_".join(str(row[r]) for r in row if r in group_key)


def get_scenario_data_csv(csv_file_path, test_scenario_id):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if test_scenario_id == row["test_scenario_id"]:
                new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def get_each_line_data_csv(csv_file_path):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def select_csv_strategy(csv_file_name, scenario, country, service, method, version):
    strategy = get_csv_strategy(country, service, method, version)
    cvs_file = os.path.join(os.getcwd(), "datasource", csv_file_name + ".csv")
    if os.path.exists(cvs_file):
        if str(strategy) == "scenario_line":
            csv_data = get_scenario_data_csv(cvs_file, scenario)
        elif str(strategy) == "single_line":
            csv_data = get_each_line_data_csv(cvs_file)
        elif str(strategy) == "multiple_lines":
            config = get_config_from_version(country, service, method, version, 'multiple_line_config')
            csv_data = load_csv_multiple_lines(cvs_file, **config)
        elif str(strategy) == "all_in":
            csv_data = load_csv(cvs_file)
        elif str(strategy) == "mixed_random_csv":
            csv_data = load_csv_and_param_keys(cvs_file, country, service, method, version)
        else:
            csv_data = load_csv(cvs_file)
        return csv_data
    else:
        raise FileNotFoundError("File does not exist in the path {0}".format(cvs_file))


def converter_pandas_csv_json(data_path):
    df = pd.read_csv(data_path)
    new_json = df.to_json(orient='records')
    return new_json
