import os
from collections import defaultdict
import yaml
import argparse
import random
import sys
from faker import Faker
from datetime import datetime, timedelta
from commons.stringManipulation import split_string_after, generate_random_number



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
    parser.add_argument('-SERVICES', help='services', dest='services')
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
        config_flow_file = read_yml_file("flow")
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
        config.flow.sort(key=lambda e: e[1]['execution_order'] if 'execution_order' in e[1] else 0)
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
    if config.environment.get("countries").get(country).get("services").get(service).get(method) is not None:
        return True
    else:
        return False


def check_if_config_version_exist(country, service, method, version):
    if config.environment.get("countries").get(country).get("services").get(service).get(method).get(
            "versions").get(version) is not None:
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
    if zip_payload is not None:
        return zip_payload
    return True


def is_request_through_middleware_api(country, service, method):
    request_through_middleware_api = get_config_from_method(country, service, method, "request_through_middleware_api")
    return request_through_middleware_api


def get_auth_payload(country, service, method):
    payload = "grant_type=" + str(
        get_auth_grant_type(country, service, method)) + "&client_id=" + str(
        get_auth_client_id(country, service, method)) + "&scope=" + str(
        get_auth_scope(country, service, method)) + "&client_secret=" + str(
        get_auth_client_secret(country, service, method)) + ""
    return payload


def get_auth_token(country, service, method):
    return str(get_config_from_method(country, service, method, "auth_token"))


def get_userId(country, service, method):
    if is_request_through_middleware_api(country, service, method):
        Id = str(get_config_from_country(country, "middleware_api_Id"))
        return Id
    else:
        Id = str(get_config_from_method(country, service, method, "Id"))
        return Id


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


def get_url(country, service, method, version):
    if is_request_through_middleware_api(country, service, method):
        url = get_config_from_version(country, service, method, version, "middleware_api_url")
        return url
    else:
        url = get_config_from_version(country, service, method, version, "url")
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
    if country in ['ar', 'co', 'do', 'ec', 'hn', 'pa', 'pe', 'py', 'sv', 'uy']:
        selected_fake_data = 'es'
    elif country == 'br':
        selected_fake_data = 'pt_BR'
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
    language = define_country_fake_data(country)
    fake = Faker(language)
    param_keys = get_config_from_version(country, service, method, version, "param_keys")
    params = param_keys.replace(" ", "")
    id_prefix = get_id_prefix(country, service, method, version)
    # using strip() and split()  methods
    if params != 'None' and params != 'none':
        result = dict((key.strip(), value.strip())
                      for key, value in (element.split(':')
                                         for element in params.split(',')))
        for key, value in result.items():
            if value[:2] == 'id':
                if split_string_after(value, value[:2]):
                    chars_number = int(split_string_after(value, value[:2]))
                    result[key] = ''.join(
                        id_prefix + "-" + service.upper() + "-" + method.upper() + "-" + version.upper() + "-" + str(
                            generate_random_number(chars_number)))
                else:
                    result[key] = id_prefix + "-" + service.upper() + "-" + method.upper() + "-" + version.upper() \
                                  + "-" + str(random.randrange(10000000))
            elif value == 'prefix':
                result[key] = id_prefix
            elif value == 'cpf':
                for _ in range(1):
                    result[key] = fake.cpf()
            elif value == 'cnpj':
                for _ in range(1):
                    result[key] = fake.cnpj()
            elif value == 'name':
                for _ in range(1):
                    if key.upper() == 'FULLNAME' or key.upper() == 'FULL_NAME' or key.upper() == 'FULL-NAME':
                        result[key] = fake.first_name() + " " + fake.last_name()
                    elif key.upper() == 'LASTNAME' or key.upper() == 'LAST_NAME' or key.upper() == 'LAST-NAME':
                        result[key] = fake.last_name()
                    elif key.upper() == 'FIRSTNAME' or key.upper() == 'FIRST_NAME' or key.upper() == 'FIRST-NAME':
                        result[key] = fake.first_name()
            elif value == 'first_name':
                for _ in range(1):
                    result[key] = fake.first_name()
            elif value == 'address':
                for _ in range(1):
                    result[key] = fake.street_suffix() + " " + fake.street_name()
            elif value == 'city':
                for _ in range(1):
                    result[key] = fake.city()
            elif value == 'state':
                for _ in range(1):
                    result[key] = fake.state()
            elif value == 'state_abbr':
                for _ in range(1):
                    result[key] = fake.state_abbr()
            elif value == 'zipcode':
                for _ in range(1):
                    result[key] = fake.postcode()
            elif value == 'phone':
                for _ in range(1):
                    result[key] = fake.msisdn()
            elif value == 'ssn':
                for _ in range(1):
                    result[key] = fake.ssn()
            elif value == 'company_name':
                for _ in range(1):
                    result[key] = fake.company() + "." + fake.company_suffix()
            elif value[:7] == 'integer':
                if split_string_after(value, value[:7]):
                    chars_number = int(split_string_after(value, value[:7]))
                    result[key] = generate_random_number(chars_number)
                else:
                    result[key] = str(random.randrange(10000000))
            elif value == 'account_name':
                result[key] = id_prefix + "-" + str(random.randrange(10000000))
            elif value == 'float':
                result[key] = round(random.uniform(1.0, 999.9), 2)
            elif value == 'email':
                result[key] = 'test_email_' + str(random.randrange(10000000)) + '@bees.com'
            elif value == 'dateToday':
                result[key] = datetime.today()
            elif value[:9] == 'startDate':
                days = 0
                if split_string_after(value, value[:11]):
                    days = int(split_string_after(value, value[:11]))
                result[key] = (datetime.now() + timedelta(days=days)).strftime("%m-%d-%YT%H:%M:%S.000Z")
            elif value[:7] == 'endDate':
                days = 0
                if split_string_after(value, value[:9]):
                    days = int(split_string_after(value, value[:9]))
                result[key] = (datetime.now() + timedelta(days=days)).strftime("%m-%d-%YT%H:%M:%S.000Z")
                #result[key] = time.strftime("%m/%d/%Y, %H:%M:%S")
            else:
                print(
                    'The type for the key "' + key + '" cannot be generate by the method "get_param_keys". Please '
                                                     'choose the correct type or add the new type.')
        return result


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
