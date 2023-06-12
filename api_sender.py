import sys
import pandas as pd
from commons.jsonDataBuilder import read_scenario_from_json
from commons.requestBuilder import send_request
from commons.utils import random_data_generator
from environment import args, get_entities, get_countries, get_methods, get_versions, get_template_name, \
    get_data_source, get_csv_scenario, check_if_config_country_exist, check_if_config_service_exist, \
    check_if_config_method_exist, check_if_config_version_exist, define_country_fake_data, get_id_prefix


def generate_data_flow(execution_flow):
    flow_list = list()
    final_random_data = dict()
    new_flow = dict()
    for item in execution_flow:
        country = item[0]
        service = item[1]
        method = item[2]
        version = item[3]
        prefix = get_id_prefix(country, service, method, version)
        keys = read_scenario_from_json("scenario",  service, "flow/test.json")
        if keys is not None:
            for key in keys:
                index = 0
                quantity = key["quantity"]
                related_keys = key["related_keys"]
                data_type = key["type"]
                parent_key = key["parent_key"]
                while index < quantity:
                    random_data = dict()
                    random_data[parent_key+str(index)] = data_type
                    random_data_generator(random_data, define_country_fake_data(country), prefix)
                    for r in related_keys:
                        final_random_data[r + str(index)] = random_data[parent_key+str(index)]
                    index = index + 1
    flow_list.append(final_random_data)
    for item in flow_list:
        for k in item:
            new_flow.setdefault(k, []).append(item[k])
    df = pd.DataFrame.from_dict(new_flow, orient='index')
    df = df.transpose()
    new_flow = df.fillna(method="ffill").to_dict("records")
    return new_flow



def get_execution_list(arguments):
    execution_flow = list()
    failure_report = list()
    countries = get_countries() if arguments.countries is None else arguments.countries.split(",")
    for country in countries:
        if check_if_config_country_exist(country) is True:
            entities = get_entities(country) if arguments.entities is None else arguments.entities.split(",")
            for service in services:
                if check_if_config_service_exist(country, service) is True:
                    methods = get_methods(country, service) if arguments.methods is None else arguments.methods.split(
                        ",")
                    for method in methods:
                        if check_if_config_method_exist(country, service, method) is True:
                            versions = get_versions(country, service,
                                                    method) if arguments.versions is None else arguments.versions.split(
                                ",")
                            for version in versions:
                                if check_if_config_version_exist(country, service, method, version) is True:
                                    execution_flow.append([country, service, method, version])
                                else:
                                    message = "The version " + version.upper() + " from the method " + method.upper() + " in the service scope " + service.upper() + " from the country zone" + country.upper() + " isn't configure in the configuration yaml file."
                                    failure_report.append(message)
                        else:
                            message = "The method " + method.upper() + " in the service scope " + service.upper() + " from the country zone " + country.upper() + " isn't configure in the configuration yaml file."
                            failure_report.append(message)
                else:
                    message = "The service scope " + service.upper() + " from the country zone " + country.upper() + " isn't configure in the configuration yaml file."
                    failure_report.append(message)
        else:
            message = "The country zone " + country.upper() + " isn't configure in the configuration yaml file."
            failure_report.append(message)
    flow_toggle = False if arguments.flow is None else True
    return flow_toggle, execution_flow, failure_report


def api_sender_exec(execution_flow, data):
    for item in execution_flow:
        country = item[0]
        service = item[1]
        method = item[2]
        version = item[3]
        print("Executing the country: ", country.upper())
        print("Executing the service: ", service.upper())
        print("Executing the method: ", method.upper())
        print("Executing the version: ", version.upper())
        template_name = get_template_name(country, service, method, version)
        data_source = get_data_source(country, service, method, version)
        csv_scenario = get_csv_scenario(country, service, method, version)
        if csv_scenario:
            for scenario in csv_scenario:
                send_request(template_name, data_source, data, scenario, country, service, method,
                             version)
        else:
            send_request(template_name, data_source, data, None, country, service, method,
                         version)


if __name__ == '__main__':
    try:
        flow, execution_list, report_list = get_execution_list(args)
        if flow:
            data_flow = generate_data_flow(execution_list)
        else:
            data_flow = None
        api_sender_exec(execution_list, data_flow)
        for report in report_list:
            print(report)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
