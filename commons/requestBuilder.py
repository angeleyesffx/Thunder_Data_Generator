import gzip
import os
import time
import calendar
import io
import uuid
import zlib
import requests
from functools import reduce

from commons.jsonDataBuilder import write_json_file
from commons.payloadBuilder import create_payload, create_middleware_api_payload, data_and_header_creation
from commons.csvDataBuilder import write_responses_in_csv
from environment import get_base_url, get_amount_data_mass, is_request_through_middleware_api, get_auth_payload, \
    get_auth_url, get_auth_method, get_config_from_version, get_id_prefix, get_auth_type, get_auth_token, \
    get_execute_flag, get_timezone, get_zip_payload


def response_from_auth(method, url, payload):
    message = "\nGetting Token Authentication..."
    data_unique_id = "Token-Auth" + method
    headers = {
        'data_unique_id': data_unique_id,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    if not get_execute_flag():
        message = "\nUsing Fake Token Authentication..."
        data={"access_token": "TOKEN_FAKE"}
        return data, message
    else:
        auth_tentative_count = 1
        while True:
            #Tratar o debug de token!!
            print("method:"+method, "url:"+url)
            print("\npayload: ", payload)
            print("\nheaders:", headers)
            response = select_request("",method, url, "", payload, headers)
            print("\nresponse:", response.content)
            if response.status_code == 200:
                if method is not None:
                    if response is not None:
                        data = response.json()
                        return data, message
                    else:
                        print("Auth wasn't able to be execute through the method " + str(method) + ". Check your configuration yml "                                                                                             "and try again.")
                break
            else:
                if auth_tentative_count < 1:

                    print("AUTHENTICATION TRY: " + str(auth_tentative_count))
                    auth_tentative_count = auth_tentative_count + 1
                else:

                    print("AUTHENTICATION TRY: " + str(auth_tentative_count))
                    print("AUTHENTICATION FAILED!!! CHECK IF THE AUTHENTICATION SERVICE IS WORKING AND TRY AGAIN.")
                    break


def get_access_token(key, method, url, payload):
    data, message = response_from_auth(method, url, payload)
    print(message)
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
    data_unique_id = "TestData-" + id_prefix + "-" + country.upper() + "-" + method.upper() + "-" + version.upper() + "-" + str(
        uuid.uuid4().hex)
    timezone = get_timezone(country)
    zip_payload_needed = get_zip_payload(country, service, method, version)
    content_encoding = "gzip" if zip_payload_needed else ""
    headers = {
        "data_unique_id": data_unique_id,
        "Accept-Language": "en",
        "Authorization": "{} {}".format(auth_type, token),
        "Content-Type": "application/json",
        "accept": "application/json",
        "country": country.upper(),
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


def send_request(template_name, data_source, data_flow, scenario, country, service, method, version):
    amount_data_mass = get_amount_data_mass(country, service, method, version)
    url = get_base_url(country, service, method, version)
    data, data_header = data_and_header_creation(data_source, data_flow, scenario, country, service, method, version,
                                                 amount_data_mass)
    multiple_request = get_config_from_version(country, service, method, version, "multiple_request")
    request_through_middleware_api = is_request_through_middleware_api(country, service, method)
    headers = create_header(data_header, country, service, method, version)
    #print("headers0", headers)
    zip_payload_needed = get_zip_payload(country, service, method, version)
    if request_through_middleware_api:
        #print("headers01", headers)
        payload = create_middleware_api_payload(template_name, data, multiple_request, country, service, method, version)
    elif not request_through_middleware_api and method == "get":
        payload = data
    else:
        payload = create_payload(template_name, data, multiple_request)
    if multiple_request and type(payload) is list:
        payload = [zip_payload(body) if zip_payload_needed else body for body in payload]
    else:
        headers = reduce(lambda a, b: dict(a, **b), headers)
        payload = zip_payload(payload) if zip_payload_needed else payload
    if not get_execute_flag():
        request_name = country + "-" + service + "-" + method + "-" + version
        print_request_and_exit(request_name, method, url, headers, payload, zip_payload_needed)
    else:
        request_name = country + "-" + service + "-" + method + "-" + version
        response = select_request(request_name, method, url, data, payload, headers, multiple_request)
        print("Send the " + method.upper() + " request version " + version.upper() + " to the " + country.upper() + " zone")
        print("Service: ", service.upper())
        evaluate_response(payload, response, request_name, multiple_request, request_through_generic_relay)


def select_request(request_name, method, url, data, payload, headers, multiple_request=False):
    # This method is responsible for create only one body for method
    if method == "post":
        if multiple_request:
            response = get_multiple_requests(method, url, data, headers, payload, request_name)
        else:
            response = requests.post(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "put":
        if multiple_request:
            response = get_multiple_requests(method, url, data, headers, payload, request_name)
        else:
            response = requests.put(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "delete":
        if multiple_request:
            response = get_multiple_requests(method, url, data, headers, payload, request_name)
        else:
            response = requests.delete(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "patch":
        if multiple_request:
            response = get_multiple_requests(method, url, data, headers, payload, request_name)
        else:
            response = requests.patch(url, data=payload, headers=headers, verify=False)
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


def get_multiple_requests(method, url, data, headers, payload, request_name):
    response = []
    # for d in data:
    # url_list.append(str(url.format(d.get("user_id"))))
    for idx, e in enumerate(payload):
        if type(headers) is list:
            new_headers = headers[idx]
            url_list = url.format(data[idx].get("user_id"))
        else:
            new_headers = headers
            url_list = url
        new_headers['data_unique_id'] = f"{new_headers['data_unique_id']}_part_{idx + 1}_of_{len(payload)}"
        new_headers['x-timestamp'] = str(calendar.timegm(time.gmtime()))
        response.append(requests.request(method, url_list, data=e, headers=new_headers))
        os.system('clear')
        print("Sending data_unique_id: " + new_headers['data_unique_id'])
        write_responses_in_csv(e, new_headers['data_unique_id'], request_name, True, False)
    return response


def evaluate_response(payload, responses, request_name, multiple_request, request_through_middleware_api):
    if type(responses) == list:
        for idx, response in enumerate(responses):
            print_result(payload[idx], response, request_name, multiple_request, request_through_middleware_api)
    else:
        print_result(payload, responses, request_name, multiple_request, request_through_middleware_api)


def print_request_and_exit(request_name, method, url, headers, body_request, zip_payload_needed):
    print('\n\n\t*************************** DEBUG MODE *******************************')
    print('\t  This mode use a fake token and no request made to any endpoint!!!   ')
    print('\t  Add the -e flag to the command line to really execute the requests ')
    print('\t**********************************************************************\n')
    if type(body_request) is not list:
        unzipped_payload = zlib.decompress(body_request, 16 + zlib.MAX_WBITS) if zip_payload_needed else body_request
        if type(unzipped_payload) is not bytes:
            unzipped_payload = bytearray(unzipped_payload, "utf-8")
        print(f'METHOD: {method}\n')
        print(f'URL: {url}\n')
        print(f'HEADERS: \n\n{headers}\n')
        print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')
        write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name)
    else:
        count = 1
        for req in body_request:
            unzipped_payload = zlib.decompress(req, 16 + zlib.MAX_WBITS) if zip_payload_needed else req
            if type(unzipped_payload) is not bytes:
                unzipped_payload = bytearray(unzipped_payload, "utf-8")
            print(f'METHOD: {method}\n')
            print(f'URL: {url}\n')
            print(f'HEADERS: \n\n{headers}\n')
            print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')
            write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name+"req"+str(count))
            count = count+1



def print_result(payload, response, request_name, multiple_request, request_through_middleware_api):
    if response.status_code == 400:
        print("Something is wrong or the country is not supported\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload)
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()))
        print("RESPONSE: ", response.content)
        print("DATA UNIQUE ID: ", response.request.headers.get('data_unique_id'))
        print("\n")
    elif response.status_code == 401:
        print("Unauthorized: Check your credential\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload)
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()))
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 403:
        print("The authorization is denied!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload)
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()))
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 404:
        print("404 Not Found!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload)
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()))
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 500:
        print("Internal Server Error!!!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload)
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()))
        print("RESPONSE: ", response.content)
        print("\n")
    else:
        print("Successfully Execution!!!\n")
        print("RESPONSE STATUS: ", response.status_code)
        print("HEADERS: ", response.request.headers)
        print("\n")
        print("DATA UNIQUE ID: ", response.request.headers.get('data_unique_id'))
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace('', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', ''))
        print("\n")
        write_responses_in_csv(payload, response.request.headers.get('data_unique_id'), request_name,
                               multiple_request,
                               request_through_middleware_api)
        print("Check the report with the data unique id in request_results folder")
