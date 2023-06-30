import sys
import uuid
import pandas as pd
from commons.jsonDataBuilder import read_scenario_from_json
from commons.payloadBuilder import data_and_header_creation, create_payload
from commons.requestBuilder import send_request, create_header
from commons.utils import random_data_generator
from environment import args, get_services, get_countries, get_methods, get_versions, get_template_name, \
    get_data_source, get_csv_scenario, check_if_config_country_exist, check_if_config_service_exist, \
    check_if_config_method_exist, check_if_config_version_exist, define_country_fake_data, get_id_prefix, \
    is_request_through_middleware_api, get_config_from_version, get_amount_data_mass, get_base_url, get_zip_payload, \
    get_auth_url, \
    get_auth_method, get_auth_type, get_timezone, get_auth_token, get_auth_payload, get_param_keys, get_static_params, \
    get_csv_strategy


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
        keys = read_scenario_from_json("scenario", service, "flow/scenario.json")
        if keys is not None:
            for key in keys:
                index = 0
                quantity = key["quantity"]
                related_keys = key["related_keys"]
                data_type = key["type"]
                parent_key = key["parent_key"]
                while index < quantity:
                    random_data = dict()
                    random_data[parent_key + str(index)] = data_type
                    random_data_generator(random_data, define_country_fake_data(country), prefix)
                    for r in related_keys:
                        final_random_data[r + str(index)] = random_data[parent_key + str(index)]
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
            services = get_services(country) if arguments.services is None else arguments.services.split(",")
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
                                    message = "The version " + version.upper() + " from the method " + method.upper() + " in the service scope " + service.upper() + " from the country zone " + country.upper() + " isn't configure in the configuration yaml file."
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


def arrange_header(data_header, prefix, country, service, method, version, zip_payload_needed):
    request_trace_id = "ThunderData-" + prefix + "-" + country.upper() + "-" + method.upper() + "-" + \
                       version.upper() + "-" + str(uuid.uuid4().hex)
    timezone = get_timezone(country)
    auth_url = get_auth_url(country, service, method)
    auth_method = get_auth_method(country, service, method)
    auth_type = get_auth_type(country, service, method)
    auth_token = get_auth_token(country, service, method)
    auth_payload = get_auth_payload(country, service, method)
    auth_header = {"requestTraceId": request_trace_id, "country": country.upper(), "timezone": timezone}
    header = create_header(data_header, auth_url, auth_method, auth_type, auth_payload, auth_token, request_trace_id,
                           auth_header, zip_payload_needed)
    return header


def arrange_payload(data, country, service, method, version, multiple_request,
                    request_through_middleware_api):
    template_name = get_template_name(country, service, method, version)
    payload = create_payload(template_name, data, service, method, version, multiple_request,
                             request_through_middleware_api)
    return payload


def arrange_data(prefix, scenario, data_flow, country, service, method, version):
    strategy = get_csv_strategy(country, service, method, version)
    data_source = get_data_source(country, service, method, version)
    param_keys = get_param_keys(country, service, method, version)
    static_params = get_static_params(country, service, method, version)
    amount_data_mass = get_amount_data_mass(country, service, method, version)
    data, data_header = data_and_header_creation(strategy, data_source, country, prefix, scenario,
                                                 data_flow, param_keys, static_params, amount_data_mass)
    return data, data_header


def thunder_exec(execution_flow, data_flow):
    for item in execution_flow:
        country = item[0]
        service = item[1]
        method = item[2]
        version = item[3]
        print("Executing the country: ", country.upper())
        print("Executing the service: ", service.upper())
        print("Executing the method: ", method.upper())
        print("Executing the version: ", version.upper())
        csv_scenario = get_csv_scenario(country, service, method, version)
        url = get_base_url(country, service, method, version)
        multiple_request = get_config_from_version(country, service, method, version, "multiple_request")
        request_through_middleware_api = is_request_through_middleware_api(country, service, method)
        zip_payload_needed = get_zip_payload(country, service, method, version)
        request_name = country + "-" + service + "-" + method + "-" + version
        prefix = get_id_prefix(country, service, method, version)
        print(
            "Send the " + method.upper() + " request version " + version.upper() + " to the " + country.upper() + " zone")
        print("service: ", service.upper())
        if not csv_scenario:
            csv_scenario = [None]
        for scenario in csv_scenario:
            data, data_header = arrange_data(prefix, scenario, data_flow, country, service, method, version)
            headers = arrange_header(data_header, prefix, country, service, method, version, zip_payload_needed)
            payload = arrange_payload(data, country, service, method, version, multiple_request,
                                      request_through_middleware_api)
            send_request(request_name, method, url, headers, payload, data, multiple_request,
                         request_through_middleware_api,
                         zip_payload_needed)

if __name__ == '__main__':
    try:
        flow, execution_list, report_list = get_execution_list(args)
        data_flow = None
        if flow:
            data_flow = generate_data_flow(execution_list)

        thunder_exec(execution_list, data_flow)
        for report in report_list:
            print(report)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
