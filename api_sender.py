import sys
from commons.requestBuilder import send_request
from environment import args, get_services, get_countries, get_methods, get_versions, get_template_name, \
    get_data_source, get_csv_scenario, check_if_config_country_exist, check_if_config_service_exist, \
    check_if_config_method_exist, check_if_config_version_exist


def get_env(arguments):
    countries = get_countries() if arguments.countries is None else arguments.countries.split(",")
    print("Executing script to the countries in the list: ", countries)
    for country in countries:
        if check_if_config_country_exist(country) is True:
            print("Executing the country: ", country.upper())
            services = get_services(country) if arguments.services is None else arguments.services.split(",")
            print("Executing script to the services in the list: ", services)
            for service in services:
                if check_if_config_service_exist(country, service) is True:
                    print("Executing the service: ", service.upper())
                    methods = get_methods(country, service) if arguments.methods is None else arguments.methods.split(
                        ",")
                    print("Executing script to the methods in the list: ", methods)
                    for method in methods:
                        if check_if_config_method_exist(country, service, method) is True:
                            print("Executing the method: ", method.upper())
                            versions = get_versions(country, service,
                                                    method) if arguments.versions is None else arguments.versions.split(
                                ",")
                            print("Executing script to the versions in the list: ", versions)
                            for version in versions:
                                if check_if_config_version_exist(country, service, method, version) is True:
                                    print("Executing the version: ", version.upper())
                                    template_name = get_template_name(country, service, method, version)
                                    data_source = get_data_source(country, service, method, version)
                                    csv_scenario = get_csv_scenario(country, service, method, version)
                                    if csv_scenario:
                                        for scenario in csv_scenario:
                                            send_request(template_name, data_source, scenario, country, service, method,
                                                         version)
                                    else:
                                        send_request(template_name, data_source, None, country, service, method, version)
                                else:
                                    print(
                                        "The version " + version.upper() + " from the method " + method.upper() + " in the service scope " + service.upper() + " from the country" + country.upper() + " isn't configure in the configuration yaml file.")
                        else:
                            print(
                                "The method " + method.upper() + " in the service scope " + service.upper() + " from the country " + country.upper() + " isn't configure in the configuration yaml file.")
                else:
                    print(
                        "The service scope " + service.upper() + " from the country " + country.upper() + " isn't configure in the configuration yaml file.")
        else:
            print("The country" + country.upper() + " isn't configure in the configuration yaml file.")


if __name__ == '__main__':

    try:
        get_env(args)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
import sys
from commons.requestBuilder import send_request
from environment import args, get_services, get_countries, get_methods, get_versions, get_template_name, \
    get_data_source, get_csv_scenario, check_if_config_country_exist, check_if_config_service_exist, \
    check_if_config_method_exist, check_if_config_version_exist


def get_env(arguments):
    countries = get_countries() if arguments.countries is None else arguments.countries.split(",")
    print("Executing script to the countries in the list: ", countries)
    for country in countries:
        if check_if_config_country_exist(country) is True:
            print("Executing the country: ", country.upper())
            services = get_services(country) if arguments.services is None else arguments.services.split(",")
            print("Executing script to the services in the list: ", services)
            for service in services:
                if check_if_config_service_exist(country, service) is True:
                    print("Executing the service: ", service.upper())
                    methods = get_methods(country, service) if arguments.methods is None else arguments.methods.split(
                        ",")
                    print("Executing script to the methods in the list: ", methods)
                    for method in methods:
                        if check_if_config_method_exist(country, service, method) is True:
                            print("Executing the method: ", method.upper())
                            versions = get_versions(country, service,
                                                    method) if arguments.versions is None else arguments.versions.split(
                                ",")
                            print("Executing script to the versions in the list: ", versions)
                            for version in versions:
                                if check_if_config_version_exist(country, service, method, version) is True:
                                    print("Executing the version: ", version.upper())
                                    template_name = get_template_name(country, service, method, version)
                                    data_source = get_data_source(country, service, method, version)
                                    csv_scenario = get_csv_scenario(country, service, method, version)
                                    if csv_scenario:
                                        for scenario in csv_scenario:
                                            send_request(template_name, data_source, scenario, country, service, method,
                                                         version)
                                    else:
                                        send_request(template_name, data_source, None, country, service, method, version)
                                else:
                                    print(
                                        "The version " + version.upper() + " from the method " + method.upper() + " in the service scope " + service.upper() + " from the country" + country.upper() + " isn't configure in the configuration yaml file.")
                        else:
                            print(
                                "The method " + method.upper() + " in the service scope " + service.upper() + " from the country " + country.upper() + " isn't configure in the configuration yaml file.")
                else:
                    print(
                        "The service scope " + service.upper() + " from the country " + country.upper() + " isn't configure in the configuration yaml file.")
        else:
            print("The country" + country.upper() + " isn't configure in the configuration yaml file.")


if __name__ == '__main__':

    try:
        get_env(args)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
