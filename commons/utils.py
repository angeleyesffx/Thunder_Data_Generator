import os
from faker import Faker
import uuid
from datetime import datetime, timedelta
from commons.stringManipulation import split_string_after, generate_random_number
import random


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(os.path.join(os.getcwd(), folder_path))


def delete_file(file_path):
    if file_exists(file_path):
        os.remove(file_path)


def file_exists(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False


def random_data_generator(param_dict, language, prefix):
    fake = Faker(language)
    for key, value in param_dict.items():
        if value[:4] == 'uuid':
            param_dict[key] = str(uuid.uuid4())
        elif value[:8] == 'uuid_hex':
            param_dict[key] = param_dict.uuid4().hex
        elif value[:4] == 'dcid':
            param_dict[key] = ''.join("DC-" + str(uuid.uuid4()))
        elif value[:6] == 'dealid':
            param_dict[key] = ''.join("DEAL-" + prefix + str(generate_random_number(10)))
        elif value[:2] == 'id':
            if split_string_after(value, value[:2]):
                chars_number = int(split_string_after(value, value[:2]))
                param_dict[key] = ''.join(prefix.upper() + "-" + str(generate_random_number(chars_number)))
            else:
                param_dict[key] = prefix.upper() + "-" + str(uuid.uuid4().hex)
        elif value == 'order_id':
            param_dict[key] = "OR-" + prefix.upper() + "-" + str(uuid.uuid4().hex) + "-" + str(uuid.uuid4().hex)
        elif value[:17] == 'vendor_account_id':
            if split_string_after(value, value[:17]):
                chars_number = int(split_string_after(value, value[:17]))
                param_dict[key] = str(generate_random_number(chars_number))
            else:
                param_dict[key] = str(uuid.uuid4().hex)
        elif value == 'cpf':
            for _ in range(1):
                param_dict[key] = fake.cpf().replace(".", "").replace("-", "")
        elif value == 'cnpj':
            for _ in range(1):
                param_dict[key] = fake.cnpj().replace(".", "").replace("/", "").replace("-", "")
        elif value == 'name':
            for _ in range(1):
                if key.upper() == 'FULLNAME' or key.upper() == 'FULL_NAME' or key.upper() == 'FULL-NAME':
                    param_dict[key] = fake.first_name() + " " + fake.last_name()
                elif key.upper() == 'LASTNAME' or key.upper() == 'LAST_NAME' or key.upper() == 'LAST-NAME':
                    param_dict[key] = fake.last_name()
                elif key.upper() == 'FIRSTNAME' or key.upper() == 'FIRST_NAME' or key.upper() == 'FIRST-NAME':
                    param_dict[key] = fake.first_name()
        elif value == 'first_name':
            for _ in range(1):
                param_dict[key] = fake.first_name()
        elif value == 'last_name':
            for _ in range(1):
                param_dict[key] = fake.last_name()
        elif value == 'address':
            for _ in range(1):
                param_dict[key] = fake.street_suffix() + " " + fake.street_name()
        elif value == 'city':
            for _ in range(1):
                param_dict[key] = fake.city()
        elif value == 'state':
            for _ in range(1):
                param_dict[key] = fake.state()
        elif value == 'state_abbr':
            for _ in range(1):
                param_dict[key] = fake.state_abbr()
        elif value == 'zipcode':
            for _ in range(1):
                param_dict[key] = fake.postcode()
        elif value == 'phone':
            for _ in range(1):
                param_dict[key] = fake.msisdn()
        elif value == 'ssn':
            for _ in range(1):
                param_dict[key] = fake.ssn()
        elif value == 'company_name':
            for _ in range(1):
                param_dict[key] = fake.company() + "." + fake.company_suffix()
        elif value[:7] == 'integer':
            if split_string_after(value, value[:7]):
                chars_number = int(split_string_after(value, value[:7]))
                param_dict[key] = generate_random_number(chars_number)
            else:
                param_dict[key] = str(uuid.uuid4().hex)
        elif value == 'account_name':
            param_dict[key] = fake.company() + "-" + str(uuid.uuid4().hex)
        elif value == 'float':
            param_dict[key] = round(random.uniform(1.0, 999.9), 2)
        elif value == 'email':
            param_dict[key] = 'test_email_' + str(uuid.uuid4().hex) + '@example.com'
        elif value == 'date':
            param_dict[key] = datetime.today()
        elif value[:14] == 'expirationDate':
            if split_string_after(value, value[:14]):
                days = int(split_string_after(value, value[:14]))
                param_dict[key] = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            else:
                param_dict[key] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif value[:9] == 'startDate':
            days = 0
            if split_string_after(value, value[:9]):
                days = int(split_string_after(value, value[:9]))
            # TODO Date New Layout ISO 8601
            param_dict[key] = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            # param_dict[key] = (datetime.now() + timedelta(days=days)).strftime("%m-%d-%YT%H:%M:%S.000Z")
        elif value[:7] == 'endDate':
            days = 0
            if split_string_after(value, value[:7]):
                days = int(split_string_after(value, value[:7]))
            # TODO Date New Layout ISO 8601
            param_dict[key] = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            # param_dict[key] = (datetime.now() + timedelta(days=days)).strftime("%m-%d-%YT%H:%M:%S.000Z")
            # param_dict[key] = time.strftime("%m/%d/%Y, %H:%M:%S")
        else:
            print(
                'The type "' + value + '" for the key "' + key + '" cannot be generate by the method. Please '
                                                                 'choose the correct type or add the new type in "utils.random_data_generator".')
    return param_dict
