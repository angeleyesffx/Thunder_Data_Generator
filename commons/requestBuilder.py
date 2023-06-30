import gzip
import json
import os
import time
import calendar
import io
import zlib
import requests
from string import Template
from functools import reduce

from commons.jsonDataBuilder import write_json_file
from commons.csvDataBuilder import write_responses_in_csv
from environment import get_execute_flag


def response_from_auth(method, url, payload):
    message = "\nGetting Token Authentication..."
    request_trace_id = "TokenAuth-" + method
    headers = {
        'requestTraceId': request_trace_id,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    if not get_execute_flag():
        message = "\nUsing Fake Token Authentication..."
        data = {"access_token": "TOKEN_FAKE"}
        return data, message
    else:
        auth_tentative_count = 1
        while True:
            # Tratar o debug de token!!
            print("method:" + method, "url:" + url)
            print("\npayload: ", payload)
            print("\nheaders:", headers)
            response = select_request("", method, url, "", payload, headers)
            print("\nresponse:", response.content)
            if response.status_code == 200:
                if method is not None:
                    if response is not None:
                        data = response.json()
                        return data, message
                    else:
                        print("Auth wasn't able to be execute through the method " + str(
                            method) + ". Check your configuration yml and try again.")
                break
            else:
                if auth_tentative_count < 1:

                    print("AUTHENTICATION TRY: " + str(auth_tentative_count))
                    auth_tentative_count = auth_tentative_count + 1
                else:

                    print("AUTHENTICATION TRY: " + str(auth_tentative_count))
                    print("AUTHENTICATION FAILED!!! CHECK IF THE AUTHENTICATION SERVICE IS WORKING AND TRY AGAIN.")
                    break


def select_token_type(auth_url, auth_method, auth_type, auth_payload, token):
    if auth_type == "Bearer":
        token = get_access_token(token, auth_method, auth_url, auth_payload)
        return token
    else:
        return token


def get_access_token(key, method, url, payload):
    data, message = response_from_auth(method, url, payload)
    if key in data:
        token = data[key]
        return str(token)


def create_header(data_header, auth_url, auth_method, auth_type, auth_payload, token, request_trace_id, auth_header=None, zip_payload_needed=None):
    new_header = []
    new_token = select_token_type(auth_url, auth_method, auth_type, auth_payload, token)
    content_encoding = "gzip" if zip_payload_needed else ""
    headers = {
        "requestTraceId": request_trace_id,
        "Authorization": "{} {}".format(auth_type, new_token),
        "Content-Type": "application/json",
        "accept": "application/json",
        "x-timestamp": str(calendar.timegm(time.gmtime())),
    }

    for header in data_header:
        if auth_header:
            for key, value in auth_header.items():
                header[key] = value
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


def send_request(request_name, method, url, headers, payload, data, multiple_request=False, request_through_generic_relay=False,
                 zip_payload_needed=None):
    if multiple_request and type(payload) is list:
        payload = [zip_payload(body) if zip_payload_needed else body for body in payload]
    else:
        headers = reduce(lambda a, b: dict(a, **b), headers)
        payload = zip_payload(payload) if zip_payload_needed else payload
    if not get_execute_flag():
        print_request_and_exit(request_name, method, url, headers, payload, zip_payload_needed)
    else:
        response = select_request(request_name, method, url, data, payload, headers, multiple_request)
        evaluate_response(payload, response, request_name, multiple_request, request_through_generic_relay)
        return response


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
            try:
                del p['test_scenario_id']
            except KeyError:
                pass
            url = Template(url).substitute(p)
            response = requests.get(url, headers=headers, params=p, verify=False)
            all_responses.append(response)
        return all_responses
    else:
        print("Method " + method + " is not found")
        return None  # 0 is the default case if method is not found


def get_multiple_requests(method, url, data, headers, payload, request_name):
    response = list()
    # for d in data:
    # url_list.append(str(url.format(d.get("user_id"))))
    for idx, e in enumerate(payload):
        if type(headers) is list:
            new_headers = headers[idx]
            url_list = Template(url).substitute(data[idx]).format(data[idx].get("user_id"))
        else:
            new_headers = headers
            url_list = Template(url).substitute(data[0])
        new_headers['requestTraceId'] = f"{new_headers['requestTraceId']}_part_{idx + 1}_of_{len(payload)}"
        new_headers['x-timestamp'] = str(calendar.timegm(time.gmtime()))
        response.append(requests.request(method, url_list, data=e, headers=new_headers))
        os.system('clear')
        print("Sending RequestTraceId: " + new_headers['requestTraceId'])
    return response


def evaluate_response(payload, responses, request_name, multiple_request=False, request_through_generic_relay=False):
    if type(responses) == list:
        for idx, response in enumerate(responses):
            print_result(payload[idx], response, request_name, multiple_request, request_through_generic_relay)
    else:
        print_result(payload, responses, request_name, multiple_request, request_through_generic_relay)
    return payload

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
            print(f'METHOD: {method}\n')
            print(f'URL: {url}\n')
            print(f'HEADERS: \n\n{headers[count - 1]}\n')
            if type(unzipped_payload) is not bytes and type(unzipped_payload) is not dict:
                unzipped_payload = bytearray(unzipped_payload, "utf-8")
                print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')
                write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name + "req" + str(count))
            if type(unzipped_payload) is bytes:
                print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')
                write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name + "req" + str(count))
            if type(unzipped_payload) is dict:
                print(f'PAYLOAD: \n\n{unzipped_payload}\n')
                write_json_file(f'\n\n{unzipped_payload}\n', request_name + "req" + str(count))
            count = count + 1


def print_result(payload, response, request_name, multiple_request, request_through_generic_relay):
    print("\n")
    params = dict()
    if response.status_code == 400:
        data = response.json()
        print("Something is wrong. What could it be? Maybe the country is not supported, or something is missing on "
              "the header. Also, the configuration in the template could be wrong, and maybe the payload is a nested "
              "JSON. Check it and try again. \n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
        print("RESPONSE: ", response.content)
        print("REQUEST TRACE ID: ", response.request.headers.get('requestTraceId'))
        print("\n")
    elif response.status_code == 401:
        data = response.json()
        print("Unauthorized: Check your credential\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 403:
        data = response
        print("The Authorization is Denied!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 404:
        data = response
        print("404 Not Found!\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code == 500:
        data = response
        print("Internal Server Error!!! Check if the service that you are trying exists.\n")
        print("STATUS: ", response.status_code)
        print("URL: ", response.request.url)
        print("HEADERS: ", response.request.headers)
        print("\n")
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
        print("RESPONSE: ", response.content)
        print("\n")
    elif response.status_code in range(200, 220):
        data = response
        print("Successfully Execution!!!\n")
        print("RESPONSE STATUS: ", response.status_code)
        print("HEADERS: ", response.request.headers)
        print("\n")
        print("REQUEST TRACE ID: ", response.request.headers.get('requestTraceId'))
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
        params['requestTraceId'] = response.request.headers.get('requestTraceId')
        write_responses_in_csv(payload, request_name, params, multiple_request, request_through_generic_relay)
        print("Check the report with the requestTraceId in request_results folder")
    else:
        data = response
        print("Finished Execution!!!\n")
        print("RESPONSE STATUS: ", response.status_code)
        print("REQUEST TRACE ID: ", response.request.headers.get('requestTraceId'))
        if type(payload) is str:
            print("REQUEST: ", payload.replace('\n', '').replace(' ', ''))
        elif type(payload) is dict:
            print("REQUEST: ", json.dumps(payload).replace('\n', '').replace(' ', ''))
        else:
            print("REQUEST: ", ''.join(payload.decode("utf-8").split()).replace('\n', '').replace(' ', ''))
        print("\n")
    return data
