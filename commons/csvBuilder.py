import ast
import json
import csv
import pandas as pd
import os
import datetime

from commons.utils import delete_file, create_folder
from environment import get_data_param_keys



# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate CSV data files                                         #
# ---------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------- CSV Functions ----------------------------------------------------#




def normalize(payload, expand_all=False):
    df = pd.json_normalize(json.loads(payload) if type(payload) == str else payload)
    # get first column that contains lists
    col = df.applymap(type).astype(str).eq("<class 'list'>").all().idxmax()
    # explode list and expand embedded dictionaries
    df = df.explode(col).reset_index(drop=True)
    while expand_all and df.applymap(type).astype(str).eq("<class 'list'>").any(axis=1).all() or df.applymap(type).astype(str).eq("<class 'dict'>").any(axis=1).all():
        df = normalize(df.to_dict("records"))
    return df


def write_responses_in_csv(response, request_name, param_keys, multiple_request, request_through_generic_relay):
    tmp_list = list()
    # Define the folder path and current date
    folder_path = os.path.join(os.getcwd(), "csv_generated")
    date_time = str(datetime.date.today().fromtimestamp(datetime.datetime.now().timestamp()))
    # Create necessary folders
    create_folder(folder_path)
    create_folder(folder_path + "/" + date_time)
    # Define the file path
    file_path = os.path.join(os.getcwd(), folder_path + "/" + date_time, f"output_data-{request_name}.csv")
    if not multiple_request:
        delete_file(file_path)
    if request_through_generic_relay:
        if type(response) is list:
            for payload in response:
                generic_response = json.loads(payload)
                tmp_list.append(generic_response["payload"])
            payload_list = tmp_list
        else:
            generic_response = json.loads(response)
            payload_list = json.loads(generic_response["payload"])
    else:
        if type(response) is list:
            for payload in response:
                new_payload = json.loads(payload)
                tmp_list.append(new_payload)
            payload_list = tmp_list
        else:
            payload_list = json.loads(response)
    if type(payload_list) is dict:
        for key, value in param_keys.items():
            payload_list[key] = value
    else:
        for payload in payload_list:
            for key, value in param_keys.items():
                payload[key] = value
            tmp_list.append(payload)
        payload_list = tmp_list
    csv_writer(file_path, payload_list)
    return file_path


def csv_writer(file_path, payload):
    df = normalize(payload, expand_all=True)
    df = df.set_index('requestTraceId')
    df.to_csv(file_path, mode='a')



def load_csv(csv_file_path):
    """
    Load all lines from a csv.
    Given this csv
        account_id    sku
        80589819      BBDREN0330024M
        #$%%          BCOR!!!!!!!!!!

    If valid data is selected in test_scenario_id, the result will be:
        [
            {'account_id': '80589819', 'sku': 'BBDREN0330024M'}, {'account_id': '#$%%', 'sku': 'BCOR!!!!!!!!!!'}
        ]

     The yaml configuration file should be like this:
                csv_strategy: all_in
                csv_data_source: Some_csv_data_source
    :param csv_file_path: csv file with data sample
    :return:
    """
    new_json = []
    with open(csv_file_path, mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def load_csv_and_param_keys(country, csv_file_path, params_keys, static_params, prefix):
        new_json = []
        with open(csv_file_path, mode='r', encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                param_keys = get_data_param_keys(country, params_keys, static_params, prefix)
                row.update(param_keys)
                new_json.append((json.dumps(row, sort_keys=True)))
        return new_json


def load_csv_multiple_lines(csv_file, group_key, output_list_name, list_fields):
    """
    Load a configuration from a csv in multiple lines and group it in a single line.
    Given this csv
        deliveryCenterId	vendorItemId	quantity
        DC001	            SKU001	        10
        DC001	            SKU002	        20
        DC002	            SKU005	        50
    The result will be:
        [
            {'deliveryCenterId': 'DC001', 'inventory': [{'vendorItemId': SKU001, 'quantity': 10},
                                        {'vendorItemId': SKU002, 'quantity': 20}]},
            {'deliveryCenterId': 'DC002', 'inventory': [{'vendorItemId': SKU005, 'quantity': 10}]}
        ]

     The yaml configuration file should be like this:
                csv_strategy: multiple_lines
                multiple_request: true
                multiple_line_config:
                  group_key:
                    - deliveryCenterId
                  output_list_name: inventory
                  list_fields:
                    - vendorItemId
                    - quantity
    :param csv_file: csv file with data sample
    :param group_key: list of fields to group the data
    :param output_list_name: output column name
    :param list_fields: fields to be grouped in the list of `output_list_name`
    :return:
    """
    result = {}
    with open(csv_file, 'r', encoding="utf8") as fh:
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
    """
    Load a data scenario from a csv in a single line.
    Given this csv
        test_scenario_id   account_id    sku
        valid data         80589819      BBDREN0330024M
        invalid data       #$%%          BCOR!!!!!!!!!!

    If valid data is selected in test_scenario_id, the result will be:
        [
            {'account_id': '80589819', 'sku': 'BBDREN0330024M'}
        ]

     The yaml configuration file should be like this:
                csv_strategy: scenario_line
                csv_data_source: Some_csv_data_source
                csv_scenario: 'valid data, invalid data, empty data'
    :param csv_file_path: csv file with data sample
    :return:
    """
    new_json = []
    with open(csv_file_path, mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if test_scenario_id == row["test_scenario_id"]:
                new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def get_each_line_data_csv(csv_file_path):
    """
    Load a data scenario from a csv in a single line.
    Given this csv
         account_id    sku
         80589819      BBDREN0330024M
         #$%%          BCOR!!!!!!!!!!

    The result will be:
        [
            {'account_id': '80589819', 'sku': 'BBDREN0330024M'}
        ]

     The yaml configuration file should be like this:
                csv_strategy: single_line
                csv_data_source: Some_csv_data_source
    :param csv_file_path: csv file with data sample
    :return:
    """
    new_json = []
    with open(csv_file_path, mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def select_csv_strategy(country, csv_file_name, strategy, scenario=None, params_keys=None, static_params=None, prefix=None):
    cvs_file = os.path.join(os.getcwd(), "datasource", csv_file_name + ".csv")
    if os.path.exists(cvs_file):
        if str(strategy) == "scenario_line":
            csv_data = get_scenario_data_csv(cvs_file, scenario)
        elif str(strategy) == "single_line":
            csv_data = get_each_line_data_csv(cvs_file)
        elif str(strategy) == "all_in":
            csv_data = load_csv(cvs_file)
        elif str(strategy) == "mixed_random_csv":
            csv_data = load_csv_and_param_keys(country, cvs_file, params_keys, static_params, prefix)
        else:
            csv_data = load_csv(cvs_file)
        return csv_data
    else:
        raise FileNotFoundError("File does not exist in the path {0}".format(cvs_file))


def converter_pandas_csv_json(data_path):
    df = pd.read_csv(data_path)
    new_json = df.to_json(orient='records')
    return new_json
