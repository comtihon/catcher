import hashlib
import random
import sys
import datetime

import pytz
from faker import Faker
from catcher.utils import module_utils

random.seed()


def function_random(param):
    """
    Call `Faker <https://github.com/joke2k/faker>`_ and return it's result. Is used to generate random data.
    F.e. ::

        - echo: {from: '{{ random("email") }}', to: one.output}

    :param param: Faker's provider name.
    """
    fake = Faker()
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


def filter_astimestamp(data, date_format='%Y-%m-%d %H:%M:%S.%f', tz='UTC'):
    """
    Convert date to timestamp. Date can be either python date object or date string
    F.e. ::

        - echo: {from: '{{ date_time_var | astimestamp }}', to: two.output}

    :param data: date time object (or string representation) to be converted to a timestamp.
    :param date_format: date format (in case it is a string)
    :param tz: timezone
    """
    if isinstance(data, str):
        data = datetime.datetime.strptime(data, date_format)
    data = pytz.timezone(tz).localize(data)
    return datetime.datetime.timestamp(data)


def filter_asdate(data, date_format='%Y-%m-%d %H:%M:%S.%f', tz='UTC'):
    """
    Convert timestamp to date
    F.e. ::

        - echo: {from: '{{ timestamp_var | asdate(date_format="%Y-%m-%d") }}', to: two.output}

    :param data: timestamp to be converted to a date
    :param date_format: expected data format.
    :param tz: timezone
    """
    if isinstance(data, str):
        if '.' in data:
            data = float(data)
        else:
            data = int(data)
    dt = datetime.datetime.fromtimestamp(data)
    data = pytz.timezone(tz).localize(dt)
    return data.strftime(date_format)


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
