import gzip
import time
import calendar
import io
import requests
import random
import zlib
import sys
from functools import reduce
from commons.payloadBuilder import create_payload, create_middleware_api_payload, data_and_header_creation
from commons.csvDataBuilder import write_responses_in_csv
from environment import get_base_url, get_amount_data_mass, is_request_through_middleware_api, get_auth_payload, \
    get_auth_url, get_auth_method, get_config_from_version, get_id_prefix, get_auth_type, get_auth_token, \
    get_execute_flag, get_timezone, get_zip_payload


def response_from_auth(method, url, payload):
    data_unique_id = "TestData-" + method
    headers = {
        'uniqueId': data_unique_id,
        'Content-Type': 'application/x-www-form-urlencoded',

    }
    response = select_request(method, url, payload, headers)
    if method is not None:
        if response is not None:
            #evaluate_response(payload, response)
            data = response.json()
            return data
        else:
            print("Auth wasn't able to be execute through the method " + str(method) + ". Check your configuration yml "
                                                                                       "and try again.")


def get_access_token(key, method, url, payload):
    print("\nGetting Token Authentication...")
    data = response_from_auth(method, url, payload)
    if key in data:
        token = data[key]
        return str(token)


def create_header(data_header, country, service, method, version):
    new_header = []
    auth_url = str(get_auth_url(country, service, method))
    auth_method = str(get_auth_method(country, service, method))
    auth_payload = str(get_auth_payload(country, service, method))
    auth_type = str(get_auth_type(country, service, method))
    if is_request_through_middleware_api(country, service, method):
        token = get_access_token('access_token', auth_method, auth_url, auth_payload)
    else:
        if auth_method == 'post':
            token = get_access_token('access_token', auth_method, auth_url, auth_payload)
        else:
            token = str(get_auth_token(country, service, method))
    id_prefix = get_id_prefix(country, service, method, version)
    data_unique_id = "TestData-" + id_prefix + "-" + country.upper() + "-" + method.upper() + "-" + str(random.randrange(1000000000))
    timezone = get_timezone(country)
    zip_payload_needed = get_zip_payload(country, service, method, version)
    content_encoding = "gzip" if zip_payload_needed else ""
    headers = {
        "uniqueId": data_unique_id,
        "Accept-Language": "en",
        "Authorization": "{} {}".format(auth_type, token),
        "Content-Encoding": f"{content_encoding}",
        "Content-Type": "application/json",
        "timezone": timezone,
        "x-timestamp": str(calendar.timegm(time.gmtime()))
    }
    for header in data_header:
        new_header.append({**headers, **header})
    return new_header


def zip_payload(payload: str) -> bytes:
    file = io.BytesIO()
    g = gzip.GzipFile(fileobj=file, mode='w')
    if type(payload) is str:
        g.write(bytes(payload, "utf-8"))
    else:
        g.write(payload)
    g.close()
    return file.getvalue()


def send_request(template_name, data_source, scenario, country, service, method, version):
    amount_data_mass = get_amount_data_mass(country, service, method, version)
    url = get_base_url(country, service, method, version)
    data, data_header = data_and_header_creation(data_source, scenario, country, service, method, version, amount_data_mass)
    multiple_request = get_config_from_version(country, service, method, version, "multiple_request")
    request_through_middleware_api = is_request_through_middleware_api(country, service, method)
    zip_payload_needed = get_zip_payload(country, service, method, version)
    headers = create_header(data_header, country, service, method, version)
    if request_through_middleware_api:
        payload = create_middleware_api_payload(template_name, data, multiple_request, country, service, method, version)
    else:
        payload = create_payload(template_name, data, multiple_request)
    if method == "get":
        body_request = payload
    else:
        if multiple_request and type(payload) is list:
            body_request = [zip_payload(body) if zip_payload_needed else body for body in payload]
        else:
            headers = reduce(lambda a, b: dict(a, **b), headers)
            body_request = zip_payload(payload) if zip_payload_needed else payload
    if not get_execute_flag():
        print_request_and_exit(method, url, headers, body_request, zip_payload_needed)
    else:
        response = select_request(method, url, body_request, headers, multiple_request)
        print("Send the " + method.upper() + " request version " + version.upper() + " to the " + country.upper() + " zone")
        print("service: ", service.upper())
        request_name = country+"-"+service+"-"+method+"-"+version
        evaluate_response(payload, response, request_name, multiple_request, request_through_middleware_api)
        return response


def print_request_and_exit(method, url, headers, body_request, zip_payload_needed):
    print('\n\n*************************** DEBUG MODE ***************************')
    print('                No request made to any endpoint!!!')
    print('Add the -e flag to the command line to really execute the requests')
    print('******************************************************************\n')
    print(f'METHOD: {method}\n')
    print(f'URL: {url}\n')
    print(f'HEADERS: \n\n{headers}\n')
    if type(body_request) is not list:
        unzipped_payload = zlib.decompress(body_request, 16 + zlib.MAX_WBITS) if zip_payload_needed else body_request
        print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')
    else:
        for req in body_request:
            unzipped_payload = zlib.decompress(req, 16 + zlib.MAX_WBITS) if zip_payload_needed else req
            print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')


def get_multiple_requests(method, url, headers, payload):
    data_unique_id = headers['uniqueId']
    response = []
    for idx, e in enumerate(payload):
        headers['uniqueId'] = f"{data_unique_id}_part_{idx + 1}_of_{len(payload)}"
        headers['x-timestamp'] = str(calendar.timegm(time.gmtime()))
        response.append(requests.request(method, url, data=e, headers=headers))
    return response


def select_request(method, url, payload, headers, multiple_request=False):
    # This method is responsible for create only one body for method
    if method == "post":
        if multiple_request:
            response = get_multiple_requests(method, url, headers, payload)
        else:
            response = requests.post(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "put":
        if multiple_request:
            response = get_multiple_requests(method, url, headers, payload)
        else:
            response = requests.put(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "delete":
        if multiple_request:
            response = get_multiple_requests(method, url, headers, payload)
        else:
            response = requests.delete(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "get":
        all_responses = []
        for p in payload:
            response = requests.get(url, headers=headers, params=p, verify=False)
            all_responses.append(response)
        return all_responses
    else:
        print("Method " + method + " is not found")
        return None  # 0 is the default case if method is not found


def evaluate_response(payload, responses, request_name, multiple_request, request_through_middleware_api):
    if type(responses) == list:
        for idx, response in enumerate(responses):
            print_result(payload[idx], response, request_name, multiple_request, request_through_middleware_api)
    else:
        print_result(payload, responses, request_name, multiple_request, request_through_middleware_api)


def print_result(payload, response, request_name, multiple_request, request_through_middleware_api):
    if response.status_code == 400:
        data = response.json()
        print("Something is wrong!!!")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("REQUEST: ", payload)
        print("RESPONSE: ", response.content)
        print("UNIQUE ID: ", response.request.headers.get('uniqueId'))
        print("\n")
    elif response.status_code == 401:
        data = response.json()
        print("Unauthorized: Check your credential\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("REQUEST: ", payload)
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 403:
        data = response
        print("The authorization is denied!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("REQUEST: ", payload)
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 500:
        data = response
        print("Internal Server Error!!!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("REQUEST: ", payload)
        print("RESPONSE: ", response.content)
        print("\n")
    else:
        print("Successfully Execution!!!\n")
        print("RESPONSE STATUS: ", response.status_code)
        print("UNIQUE ID: ", response.request.headers.get('uniqueId'))
        print("REQUEST: ", payload)
        print("\n")
        write_responses_in_csv(payload, response.request.headers.get('uniqueId'), request_name, multiple_request,
                               request_through_middleware_api)
        data = response
    return data
