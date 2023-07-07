from datetime import datetime, timedelta
import random
import uuid
from faker import Faker


def generate_random_number(number_of_digits):
    if number_of_digits is "" or number_of_digits is None:
        number_of_digits = 0
    begin = int('1' + '0' * (number_of_digits - 1))
    end = int('9' * number_of_digits)
    return str(random.randrange(begin, end))


def define_country_fake_data(country):
    country_language_map = {
        "ar": "es_AR",
        "aq": "en",
        "bo": "es",
        "br": "pt_BR",
        "ca": "en_CA",
        "cl": "es_CL",
        "co": "es_CO",
        "de": "de_DE",
        "do": "es",
        "ec": "es",
        "fr": "fr_FR",
        "gb": "en_GB",
        "hn": "es",
        "jp": "ja_JP",
        "kr": "ko-KR",
        "mx": "es_MX",
        "pa": "es",
        "pe": "es",
        "pt": "pt_PT",
        "py": "es",
        "sv": "es",
        "tz": "en",
        "ug": "en",
        "uy": "es",
        "us": "en_US",
        "za": "en_ZA"
    }
    return country_language_map.get(country, "en")


def random_data_generator(param_dict, language):
    fake = Faker(language)

    def custom_id_generator(pattern):
        if pattern is "" or pattern is None:
            return ''.join(str(uuid.uuid4()))
        chars_number = int(pattern)
        return ''.join(str(generate_random_number(chars_number)))

    def custom_date_generator(days):
        if days is "" or days is None:
            days = "1"
        date = datetime.today() + timedelta(days=(int(days) - 1))
        return date.strftime("%Y-%m-%d")

    pattern_types = {
        'account_id': lambda prefix: "AC-" + prefix + str(generate_random_number(10)),
        'account_name': lambda _: fake.company() + "." + fake.company_suffix(),
        'address': lambda _: fake.street_suffix() + " " + fake.street_name(),
        'city': lambda _: fake.city(),
        'company_name': lambda _: fake.company() + "." + fake.company_suffix(),
        'country': lambda _: fake.country(),
        'country_code': lambda _: fake.country_code(),
        'cnpj': lambda _: fake.cnpj().replace(".", "").replace("/", "").replace("-", ""),
        'cpf': lambda _: fake.cpf().replace(".", "").replace("-", ""),
        'currency': lambda _: fake.currency_code(),
        'date': custom_date_generator,
        'dcc_id': lambda: "DC-" + str(uuid.uuid4()),
        'deal_id': lambda prefix: "DEAL-" + prefix + str(generate_random_number(10)),
        'email': lambda _: 'test_email_' + str(uuid.uuid4().hex) + '@example.com',
        'first_name': lambda _: fake.first_name(),
        'float': lambda _: round(random.uniform(1.0, 999.9), 2),
        'id': custom_id_generator,
        'integer': lambda pattern: generate_random_number(int(pattern)),
        'last_name': lambda _: fake.last_name(),
        'name': lambda _: fake.first_name() + " " + fake.last_name(),
        'name_prefix': lambda _: fake.prefix(),
        'name_suffix': lambda _: fake.suffix(),
        'number': lambda pattern: generate_random_number(int(pattern)),
        'order_id': lambda prefix: "OR-" + prefix.upper() + "-" + str(uuid.uuid4().hex) + "-" + str(uuid.uuid4().hex),
        'phone': lambda _: fake.msisdn(),
        'state': lambda _: fake.state(),
        'state_abbr': lambda _: fake.state_abbr(),
        'startDate': custom_date_generator,
        'street': lambda _: fake.street_name(),
        'street_number': lambda _: fake.building_number(),
        'ssn': lambda _: fake.ssn(),
        'uuid': lambda: str(uuid.uuid4()),
        'uuid_hex': lambda: uuid.uuid4().hex,
        'vendor_account_id': custom_id_generator,
        'zipcode': lambda _: fake.postcode()
    }

    for key, value_type in param_dict.items():
        prefix, _, pattern = value_type.partition('|')
        generator = pattern_types.get(prefix)

        if generator is not None:
            param_dict[key] = generator(pattern)
        else:
            print(f'The type "{value_type}" for the key "{key}" cannot be generated. '
                  f'Please choose the correct type or create a new type on method "random_data_generator".')

    return param_dict


def create_param_dict(params):
    if params not in {'None', 'none', '', None}:
        return {key.strip(): value.strip() for key, value in (element.split(':', 1) for element in params.split(','))}
    return None
