import datetime
import os
from distutils.file_util import write_file, copy_file
from os.path import join
from time import strptime, mktime

from jinja2 import Template
from pkg_resources import Requirement, resource_filename

from catcher.utils.file_utils import read_file

# This is catcher's resource. Not the test's one. See file_utils for test resources.
import catcher


def modify_resource(resource_name, params, path):
    resource_path = resource_filename(Requirement.parse(catcher.APPNAME), join('catcher/resources', resource_name))
    resource_content = read_file(resource_path)
    template = Template(resource_content)
    template.globals['now'] = datetime.datetime.utcnow
    template.globals['strptime'] = strptime
    template.globals['mktime'] = mktime
    resource_filled = template.render(params)
    with open(path, "w") as w:
        w.write(resource_filled)


def ensure_resource(resource, path):
    resource_path = join(path, resource)
    if not os.path.isfile(resource_path):
        resource = resource_filename(Requirement.parse(catcher.APPNAME), join('catcher/resources', resource))
        copy_file(resource, resource_path)
    return resource_path
