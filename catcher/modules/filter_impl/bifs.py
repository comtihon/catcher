import hashlib
import random
import sys
import datetime
import time

from faker import Faker
from catcher.utils import module_utils, misc

random.seed()


def filter_astuple(param):
    """
    Convert data to tuple
    F.e. ::

        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              query: "select status from my_table
                     where id in {{ [1, 2, 3] |astuple }}"

    :param param: data to convert
    """
    return tuple(misc.try_get_objects(param))


def filter_asint(param):
    """
    Convert data to int
    F.e. ::

        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              query: "select status from my_table
                     where id == {{ my_str_var |asint }}"

    :param param: data to convert
    """
    return int(misc.try_get_objects(param))


def filter_asfloat(param):
    """
    Convert data to float
    F.e. ::

        - check: {equals: {the: 36.6, is: '{{ "36.6" | asfloat }}'}}

    :param param: data to convert
    """
    return float(misc.try_get_objects(param))


def filter_aslist(param):
    """
    Convert data to list
    F.e. ::

        - loop:
            foreach:
                in: '{{ my_dictionary |aslist }}'
                do:
                    echo: {from: '{{ ITEM.value }}', to: '{{ ITEM.key }}.output'}

    :param param: data to convert
    """
    return list(misc.try_get_objects(param))


def filter_asdict(param):
    """
    Convert data to dict
    F.e. ::

        - check: {equals: {the: [1, 2],
                           is: '{{ ([("one", 1), ("two", 2)] | asdict).values() |aslist }}'}}

    :param param: data to convert
    """
    return dict(misc.try_get_objects(param))


def filter_asstr(param):
    """
    Convert data to string
    F.e. ::

        - check: {equals: {the: '17', is: '{{ my_int | asstr }}'}}

    :param param: data to convert
    """
    return str(misc.try_get_objects(param))


def function_random(param, locale=None):
    """
    Call `Faker <https://github.com/joke2k/faker>`_ and return it's result. Is used to generate random data.
    F.e. ::

        - echo: {from: '{{ random("email") }}', to: one.output}

    :param param: Faker's provider name.
    :param locale: Faker's locale param
    """
    fake = Faker(locale=locale)
    for modname, importer in module_utils.get_submodules_of('faker.providers'):  # add all known providers
        fake.add_provider(importer.find_module(modname).load_module(modname))
    if hasattr(fake, param):
        return getattr(fake, param)()
    else:
        raise ValueError('Unknown param to randomize: ' + param)


def filter_hash(data, alg='md5'):
    """
    Filter for hashing data.
    F.e. ::

        - echo: {from: '{{ my_var | hash("sha1") }}', to: two.output}

    :param data: data to hash
    :param alg: algorithm to use
    """
    if hasattr(hashlib, alg):
        m = getattr(hashlib, alg)()
        m.update(data.encode())
        return m.hexdigest()
    else:
        raise ValueError('Unknown algorithm: ' + data)


def function_now(date_format='%Y-%m-%d %H:%M:%S.%f'):
    """
    Get current date in a specified format.
    F.e. ::

        - echo: {from: '{{ now("%Y-%m-%d") }}', to: year.output}
    :param date_format: date format
    """
    return datetime.datetime.now().strftime(date_format)


def function_now_ts():
    """
    Get current date time in as a timestamp.
    F.e. ::

        - echo: {from: '{{ now_ts() }}', to: timestamp.output}
    """
    return round(time.time(), 6)  # from timestamp uses rounding, so we should also use it here, to make them compatible


def filter_astimestamp(data, date_format='%Y-%m-%d %H:%M:%S.%f'):
    """
    Convert date to timestamp. Date can be either python date object or date string
    F.e. ::

        - echo: {from: '{{ date_time_var | astimestamp }}', to: two.output}

    :param data: date time object (or string representation) to be converted to a timestamp.
    :param date_format: date format (in case it is a string)
    """
    if isinstance(data, str):
        data = datetime.datetime.strptime(data, date_format)
    return datetime.datetime.timestamp(data)


def filter_asdate(data, date_format='%Y-%m-%d %H:%M:%S.%f'):
    """
    Convert timestamp to date
    F.e. ::

        - echo: {from: '{{ timestamp_var | asdate(date_format="%Y-%m-%d") }}', to: two.output}

    :param data: timestamp to be converted to a date
    :param date_format: expected data format.
    """
    if isinstance(data, str):
        if '.' in data:
            data = float(data)
        else:
            data = int(data)
    return datetime.datetime.fromtimestamp(data).strftime(date_format)


def function_random_int(range_from=-sys.maxsize - 1, range_to=sys.maxsize):
    """
    Function for random number return. Output can be controlled by `range_from` and `range_to` attributes.
    F.e. ::

        - echo: {from: '{{ random_int(range_from=1) }}', to: one.output}

    """
    return random.randint(range_from, range_to)


def function_random_choice(sequence):
    """
    Function to make a random choice in a collection.
    F.e. ::

        - echo: {from: '{{ random_choice([1, 2, 3]) }}', to: one.output}

    :param sequence: collection of elements to choose from.
    """
    return random.choice(sequence)
