# pylint:disable = unused-wildcard-import
from setuptools import *
import toml
from codecs import open
from os import path
import inspect
import mimetypes

setuptools_setup = setup

# pylint: disable = function-redefined


def setup(*args, **kwargs):
    caller_directory = '.'

    try:
        caller_directory = path.abspath(path.dirname(inspect.stack()[1].filename))
    except:
        pass

    with open(path.join(caller_directory, 'pyproject.toml'), 'r', encoding='utf-8') as pptoml:
        pyproject_toml = pptoml.read()

    pyproject_data = toml.loads(pyproject_toml)

    kwargs = {**pyproject_data['project'], **kwargs}
    kwargs = _parse_kwargs(kwargs, caller_directory)

    return setuptools_setup(*args, **kwargs)


def _parse_kwargs(kwargs, caller_directory):
    long_description = kwargs.get('project', {}).get('long_description')
    if long_description and long_description.startswith('file:'):
        kwargs['project']['long_description_content_type'] = mimetypes.guess_type(
            long_description.split('file:')[-1].lower()
        )
    kwargs = _replace_files(kwargs, caller_directory)
    return kwargs


def _replace_files(kwargs, caller_directory):
    for key in kwargs.keys():
        if isinstance(kwargs[key], str) and kwargs[key].startswith('file:'):
            try:
                filename = kwargs[key].split('file:')[-1].strip()
                with open(path.join(caller_directory, filename), 'r', encoding='utf-8') as toml_file_link:
                    kwargs[key] = toml_file_link.read()
            except:
                # If we failed, just keep the value
                pass
        elif isinstance(kwargs[key], dict):
            kwargs[key] = _replace_files(kwargs[key], caller_directory)

    return kwargs
