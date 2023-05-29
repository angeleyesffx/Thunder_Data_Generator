import sys
import pandas as pd
from commons.jsonDataBuilder import read_scenario_from_json
from commons.requestBuilder import send_request
from commons.utils import random_data_generator
from environment import args, get_entities, get_countries, get_methods, get_versions, get_template_name, \
    get_data_source, get_csv_scenario, check_if_config_country_exist, check_if_config_entity_exist, \
    check_if_config_method_exist, check_if_config_version_exist, define_country_fake_data, get_id_prefix


def generate_data_flow(execution_flow):
    flow_list = list()
    random_data = dict()
    new_flow = dict()
    for item in execution_flow:
        country = item[0]
        entity = item[1]
        method = item[2]
        version = item[3]
        prefix = get_id_prefix(country, entity, method, version)
        index = 0
        keys = read_scenario_from_json("scenario",  entity, "flow/test.json")
        if keys is not None:
            for key in keys:
                quantity = key["quantity"]
                related_keys = key["related_keys"]
                data_type = key["type"]
                parent_key = key["parent_key"]
                while index < quantity:
                    random_data[parent_key] = data_type
                    flow_list.insert(index, associate_parent_key_with_related_keys(random_data_generator(random_data, define_country_fake_data(country), prefix), related_keys))
                    random_data = dict()
                    index = index + 1
    for item in flow_list:
        for k in item:
            new_flow.setdefault(k, []).append(item[k])
    df = pd.DataFrame.from_dict(new_flow, orient='index')
    df = df.transpose()
    new_flow = df.fillna(method="ffill").to_dict("records")
    return new_flow


def associate_parent_key_with_related_keys(parent_key, related_keys):
    data = dict()
    for item in parent_key:
        for key in related_keys:
            data[key] = parent_key[item]
    return data


def get_execution_list(arguments):
    execution_flow = list()
    failure_report = list()
    countries = get_countries() if arguments.countries is None else arguments.countries.split(",")
    for country in countries:
        if check_if_config_country_exist(country) is True:
            entities = get_entities(country) if arguments.entities is None else arguments.entities.split(",")
            for entity in entities:
                if check_if_config_entity_exist(country, entity) is True:
                    methods = get_methods(country, entity) if arguments.methods is None else arguments.methods.split(
                        ",")
                    for method in methods:
                        if check_if_config_method_exist(country, entity, method) is True:
                            versions = get_versions(country, entity,
                                                    method) if arguments.versions is None else arguments.versions.split(
                                ",")
                            for version in versions:
                                if check_if_config_version_exist(country, entity, method, version) is True:
                                    execution_flow.append([country, entity, method, version])
                                else:
                                    message = "The version " + version.upper() + " from the method " + method.upper() + " in the entity scope " + entity.upper() + " from the country zone" + country.upper() + " isn't configure in the configuration yaml file."
                                    failure_report.append(message)
                        else:
                            message = "The method " + method.upper() + " in the entity scope " + entity.upper() + " from the country zone " + country.upper() + " isn't configure in the configuration yaml file."
                            failure_report.append(message)
                else:
                    message = "The entity scope " + entity.upper() + " from the country zone " + country.upper() + " isn't configure in the configuration yaml file."
                    failure_report.append(message)
        else:
            message = "The country zone " + country.upper() + " isn't configure in the configuration yaml file."
            failure_report.append(message)
    flow_toggle = False if arguments.flow is None else True
    return flow_toggle, execution_flow, failure_report


def api_sender_exec(execution_flow, data):
    for item in execution_flow:
        country = item[0]
        entity = item[1]
        method = item[2]
        version = item[3]
        print("Executing the country: ", country.upper())
        print("Executing the entity: ", entity.upper())
        print("Executing the method: ", method.upper())
        print("Executing the version: ", version.upper())
        template_name = get_template_name(country, entity, method, version)
        data_source = get_data_source(country, entity, method, version)
        csv_scenario = get_csv_scenario(country, entity, method, version)
        if csv_scenario:
            for scenario in csv_scenario:
                send_request(template_name, data_source, data, scenario, country, entity, method,
                             version)
        else:
            send_request(template_name, data_source, data, None, country, entity, method,
                         version)


if __name__ == '__main__':
    try:
        flow, execution_list, report_list = get_execution_list(args)
        if flow:
            data_flow = generate_data_flow(execution_list)
        else:
            data_flow = None
        thunder_exec(execution_list, data_flow)
        for report in report_list:
            print(report)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
