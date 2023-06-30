import os
from collections import defaultdict
import yaml
import argparse
import random
import sys

from commons.utils import random_data_generator


class Config(object):
    def __init__(self, environment, flow, config_yaml, countries, services, methods, versions, execute):
        self.environment = environment
        self.flow = flow
        self.config_yaml = config_yaml
        self.countries = countries
        self.services = services
        self.methods = methods
        self.versions = versions
        self.execute = execute


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-CONFIG_YAML', help='config yaml', dest='config_yaml')
    parser.add_argument('-ENV', help='environment', dest='environment')
    parser.add_argument('-COUNTRIES', help='countries', dest='countries')
    parser.add_argument('-services', help='services', dest='services')
    parser.add_argument('-METHODS', help='methods', dest='methods')
    parser.add_argument('-VERSIONS', help='versions', dest='versions')
    parser.add_argument('-FLOW', help='flow', dest='flow')
    parser.add_argument('-e', '--execute', action='store_true', help='enable the long listing format')
    return parser.parse_args(sys.argv[1:])


args = parse_args()


def read_yml_file(yml_file_name):
    file_path = os.path.dirname(__file__) + "/" + yml_file_name + ".yml"
    if os.path.exists(file_path):
        with open(file_path) as file:
            data = yaml.full_load(file)
            file.close()
            return data
    else:
        raise FileNotFoundError("File does not exist in the path {0}".format(file_path))


def select_the_config_file(config_yaml):
    if config_yaml is None:
        config_file = read_yml_file("config")
        return config_file
    else:
        config_file = read_yml_file(config_yaml)
        return config_file


def select_the_environment(environment, config_yaml):
    environments = select_the_config_file(config_yaml)
    if environment is None:
        print("Executing DataCreation in SIT environment...")
        return environments.get("sit")
    else:
        print("Executing DataCreation in ", environment, " environment...")
        return environments.get(environment)


def select_the_execution_flow(flow):
    if flow is not None:
        config_flow_file = read_yml_file("flow/config_flow")
        return config_flow_file
    else:
        return None


config = Config(select_the_environment(args.environment, args.config_yaml), select_the_execution_flow(args.flow),
                select_the_config_file(args.config_yaml), args.countries, args.services, args.methods, args.versions,
                args.execute)


def check_for_error_ir_order(execution_flows):
    flow_counter_list = defaultdict(list)
    for execution_flow in execution_flows:
        flow_counter_list[execution_flow[1]['execution_order']].append(execution_flow[0])

    for flow_order, flow_names in flow_counter_list.items():
        if len(flow_names) > 1:
            print(f"WARN - Flows with same order '{flow_order}': {', '.join(flow_names)}")


def get_countries():
    # Get a list of Countries
    countries_list = config.countries
    if countries_list is None:
        countries = set()
        countries.update(config.environment.get("countries"))
        return sorted(countries)
    else:
        countries = countries_list.split(",")
        return countries


def get_services(country):
    # Get a list of services
    services_list = config.services
    if services_list is None and config.flow is None:
        services = set()
        services.update(config.environment.get("countries").get(country).get("services"))
        return sorted(services)
    elif services_list is None and config.flow is not None:
        execution_flow = list(config.flow.get("execution_flows").get(args.flow).items())
        check_for_error_ir_order(execution_flow)
        list(config.flow).sort(key=lambda e: e[1]['execution_order'] if 'execution_order' in e[1] else 0)
        return [value[0] for value in execution_flow]
    else:
        services = services_list.split(",")
        return services


def get_methods(country, service):
    # Get a list of Methods
    methods_list = config.methods
    if methods_list is None and config.flow is None:
        methods = set()
        methods.update(config.environment.get("countries").get(country).get("services").get(service))
        return sorted(methods)
    elif methods_list is None and config.flow is not None:
        service_methods = config.flow.get("execution_flows").get(args.flow).get(service).copy()
        service_methods.pop('execution_order')
        return sorted(service_methods.keys())
    else:
        methods = methods_list.split(",")
        return methods


def get_versions(country, service, method):
    # Get a list of Versions
    versions_list = config.versions
    if versions_list is None and config.flow is None:
        versions = set()
        versions.update(
            config.environment.get("countries").get(country).get("services").get(service).get(method).get("versions"))
        return sorted(versions)
    elif versions_list is None and config.flow is not None:
        versions = set()
        versions.update(config.flow.get("execution_flows").get(args.flow).get(service).get(method))
        return sorted(versions)
    else:
        versions = versions_list.split(",")
        return versions


def get_environment_basic_config(key):
    config_env = config.environment.get(key)
    return config_env


def get_execute_flag():
    return config.execute


def get_config_from_country(country, key):
    config_country = config.environment.get("countries").get(country).get(key)
    return config_country


def get_config_from_service(country, service, key):
    config_service = config.environment.get("countries").get(country).get("services").get(service).get(key)
    return config_service


def get_config_from_method(country, service, method, key):
    config_method = config.environment.get("countries").get(country).get("services").get(service).get(method).get(key)
    return config_method


def get_config_from_version(country, service, method, version, key):
    config_version = config.environment.get("countries").get(country).get("services").get(service).get(method).get(
        "versions").get(
        version).get(key)
    return config_version


def check_if_config_country_exist(country):
    if config.environment.get("countries").get(country) is not None:
        return True
    else:
        return False


def check_if_config_service_exist(country, service):
    return config.environment.get("countries").get(country).get("services").get(service) is not None


def check_if_config_method_exist(country, service, method):
    if config.environment.get("countries").get(country).get("services").get(service).get(method):
        return True
    else:
        return False


def check_if_config_version_exist(country, service, method, version):
    if config.environment.get("countries").get(country).get("services").get(service).get(method).get(
            "versions").get(version):
        return True
    else:
        return False


def get_timezone(country):
    timezone = config.environment.get("countries").get(country).get("timezone")
    if timezone:
        return timezone
    return "America/Louisville"


def get_base_url(country, service, method, version):
    url = str(get_environment_basic_config("base_url")) + str(get_url(country, service, method, version))
    return url


def get_zip_payload(country, service, method, version):
    zip_payload = get_config_from_version(country, service, method, version, 'zip_payload')
    return zip_payload


def is_request_through_middleware_api(country, service, method):
    request_through_middleware_api = get_config_from_method(country, service, method, "request_through_middleware_api")
    return request_through_middleware_api


def get_auth_payload(country, service, method):
    auth_token_type = get_auth_token_type(country, service, method)
    if str(auth_token_type).upper == "B2B":
        payload = "grant_type=" + str(
            get_auth_grant_type(country, service, method)) + "&client_id=" + str(
            get_auth_client_id(country, service, method)) + "&scope=" + str(
            get_auth_scope(country, service, method)) + "&client_secret=" + str(
            get_auth_client_secret(country, service, method)) + ""
    else:
            payload = "grant_type=" + str(
            get_auth_grant_type(country, service, method)) + "&client_id=" + str(
            get_auth_client_id(country, service, method)) + "&scope=" + str(
            get_auth_scope(country, service, method)) + "&client_secret=" + str(
            get_auth_client_secret(country, service, method)) + "&username=" + str(
            get_auth_username(country, service, method)) + "&password=" + str(
            get_auth_password(country, service, method)) + "&response_type=" + str(
            get_auth_response_type(country, service, method)) + ""
    return payload


def get_auth_token(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        return str(get_config_from_country(country, "middleware_api_auth_token"))
    else:
        return str(get_config_from_method(country, service, method, "auth_token"))


def get_auth_token_type(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        return str(get_config_from_country(country, "middleware_api_auth_token_type"))
    else:
        return str(get_config_from_method(country, service, method, "auth_token_type"))


def get_vendor_id(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        vendorId = str(get_config_from_country(country, "middleware_api_vendor_id"))
        return vendorId
    else:
        vendorId = str(get_config_from_method(country, service, method, "auth_vendor_id"))
        return vendorId


def get_auth_type(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_type = str(get_config_from_country(country, "middleware_api_auth_type"))
        return auth_type
    else:
        auth_type = str(get_config_from_method(country, service, method, "auth_type"))
        return auth_type


def get_auth_method(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_method = str(get_config_from_country(country, "middleware_api_auth_method"))
        return auth_method
    else:
        auth_method = str(get_config_from_method(country, service, method, "auth_method"))
        return auth_method


def get_auth_url(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_url = str(get_config_from_country(country, "middleware_api_auth_url"))
        return auth_url
    else:
        auth_url = str(get_config_from_method(country, service, method, "auth_url"))
        return auth_url


def get_auth_scope(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_scope = str(get_config_from_country(country, "middleware_api_auth_scope"))
        return auth_scope
    else:
        auth_scope = str(get_config_from_method(country, service, method, "auth_scope"))
        return auth_scope


def get_auth_grant_type(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_grant_type = str(get_config_from_country(country, "middleware_api_auth_grant_type"))
        return auth_grant_type
    else:
        auth_grant_type = str(get_config_from_method(country, service, method, "auth_grant_type"))
        return auth_grant_type


def get_auth_client_id(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_client_id = str(get_config_from_country(country, "middleware_api_auth_client_id"))
        return auth_client_id
    else:
        auth_client_id = str(get_config_from_method(country, service, method, "auth_client_id"))
        return auth_client_id


def get_auth_client_secret(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_client_secret = str(get_config_from_country(country, "middleware_api_auth_client_secret"))
        return auth_client_secret
    else:
        auth_client_secret = str(get_config_from_method(country, service, method, "auth_client_secret"))
        return auth_client_secret


def get_auth_username(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_username = str(get_config_from_country(country, "middleware_api_auth_username"))
        return auth_username
    else:
        auth_username = str(get_config_from_method(country, service, method, "auth_username"))
        return auth_username


def get_auth_password(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_password = str(get_config_from_country(country, "middleware_api_auth_password"))
        return auth_password
    else:
        auth_password = str(get_config_from_method(country, service, method, "auth_password"))
        return auth_password


def get_auth_response_type(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        auth_response_type = str(get_config_from_country(country, "middleware_api_auth_response_type"))
        return auth_response_type
    else:
        auth_response_type = str(get_config_from_method(country, service, method, "auth_response_type"))
        return auth_response_type


def get_url(country, service, method, version):
    if is_request_through_middleware_api(country, service, method):
        url = get_config_from_version(country, service, method, version, "url")
        return url
    else:
        url = get_config_from_version(country, service, method, version, "value_stream_url")
        return url


def get_supported_languages(country):
    supported_languages = get_config_from_country(country, "supported_languages")
    languages = supported_languages.replace(' ', '').split(",")
    language = random.choice(languages)
    return language


def get_id_prefix(country, service, method, version):
    id_prefix = get_config_from_version(country, service, method, version, "id_prefix")
    return id_prefix


def define_country_fake_data(country):
    if country in ['ar', 'co', 'de', 'do', 'ec', 'hn', 'pa', 'pe', 'py', 'sv', 'uy']:
        selected_fake_data = 'es'
    elif country == 'br':
        selected_fake_data = 'pt_BR'
    elif country == 'de':
        selected_fake_data = 'en_DE'
    elif country == 'ca':
        selected_fake_data = 'en_CA'
    elif country == 'gb':
        selected_fake_data = 'en_GB'
    elif country == 'mx':
        selected_fake_data = 'es_MX'
    elif country == 'pt':
        selected_fake_data = 'pt_PT'
    elif country == 'kr':
        selected_fake_data = 'ko-KR'
    elif country == 'us':
        selected_fake_data = 'en_US'
    else:
        selected_fake_data = 'en'
    return selected_fake_data


def get_param_keys(country, service, method, version):
    param_keys = get_config_from_version(country, service, method, version, "param_keys")
    if param_keys is not None:
        params = param_keys.replace(" ", "")
        return params


def get_static_params(country, service, method, version):
    static_params = get_config_from_version(country, service, method, version, "static_params")
    if static_params is not None:
        params = static_params.replace(" ", "")
        return params


def create_static_params_dict(static_params):
    # using strip() and split()  methods
    if static_params != 'None' and static_params != 'none' and static_params != '' and static_params is not None:
        result = dict((key.strip(), value.strip())
                      for key, value in (element.split('=')
                                         for element in static_params.split(',')))
        return result


def create_param_dict(params):
    # using strip() and split()  methods
    if params != 'None' and params != 'none' and params != '' and params is not None:
        result = dict((key.strip(), value.strip())
                      for key, value in (element.split(':')
                                         for element in params.split(',')))
        return result


def get_data_param_keys(country, params, static_params=None, prefix=None):
    language = define_country_fake_data(country)
    new_static_params = create_static_params_dict(static_params)
    param_dict = create_param_dict(params)
    data = None
    if static_params is not None:
        for key, value in new_static_params.items():
            param_dict[key] = value
    if param_dict is not None:
        data = random_data_generator(param_dict, language, prefix)
    return data


def get_encoding_type(country, service, method, version):
    encoding_type = get_config_from_version(country, service, method, version, "encoding_type")
    return encoding_type


def get_template_name(country, service, method, version):
    template_name = get_config_from_version(country, service, method, version, "template_name")
    return template_name


def get_data_source(country, service, method, version):
    data_name = get_config_from_version(country, service, method, version, "csv_data_source")
    return data_name


def get_csv_strategy(country, service, method, version):
    csv_strategy = get_config_from_version(country, service, method, version, "csv_strategy")
    return csv_strategy


def get_csv_scenario(country, service, method, version):
    csv_scenario = get_config_from_version(country, service, method, version, "csv_scenario")
    if not csv_scenario:
        return None
    scenarios_list = csv_scenario.replace(' ', '').split(",")
    return scenarios_list


def get_amount_data_mass(country, service, method, version):
    amount_data_mass = get_config_from_version(country, service, method, version, "amount_data_mass")
    return amount_data_mass
