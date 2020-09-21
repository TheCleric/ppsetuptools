# pylint:disable = unused-wildcard-import
from setuptools import *
import toml
from codecs import open
from os import path
import inspect
import mimetypes

setuptools_setup = setup

# pylint: disable = function-redefined
mimetype_overrides = {
    'md': 'text/markdown'
}

valid_setup_params = ['name', 'version', 'description', 'long_description', 'long_description_content_type', 'url', 'author', 'author_email',
                      'maintainer', 'maintainer_email', 'license', 'classifiers', 'keywords', 'install_requires', 'include_package_data', 'extras_require',
                      'zip_safe', 'packages', 'scripts', 'package_data', 'data_files', 'entry_points']


def setup(*args, **kwargs):
    caller_directory = '.'

    try:
        caller_directory = path.abspath(path.dirname(inspect.stack()[1].filename))
    except:
        pass

    with open(path.join(caller_directory, 'pyproject.toml'), 'r', encoding='utf-8') as pptoml:
        pyproject_toml = pptoml.read()

    pyproject_data = toml.loads(pyproject_toml)

    kwargs_copy = kwargs.copy()
    kwargs_copy.update(_filter_dict(pyproject_data['project'], valid_setup_params))

    kwargs = _parse_kwargs(kwargs_copy, caller_directory)

    print('Calling setuptools.setup with args: {}'.format(args))
    print('And kwargs:')
    print(kwargs)

    return setuptools_setup(*args, **kwargs)


def _filter_dict(kwargs, allowed_params):
    return {k: v for k, v in kwargs.items() if k in allowed_params}


def _parse_kwargs(kwargs, caller_directory):
    long_description = kwargs.get('long_description')
    if long_description and long_description.startswith('file:'):
        kwargs['long_description_content_type'] = _get_mimetype(long_description.split('file:')[-1].lower())
        print('long_description is a file reference: "{}"'.format(long_description))
        print('Assigning long_description_content_type of "{}"'.format(
            kwargs['long_description_content_type'])
        )
    kwargs = _replace_files(kwargs, caller_directory)
    return kwargs


def _replace_files(kwargs, caller_directory):
    for key in kwargs.keys():
        if isinstance(kwargs[key], str) and kwargs[key].startswith('file:'):
            try:
                filename = kwargs[key].split('file:')[-1].strip()
                with open(path.join(caller_directory, filename), 'r', encoding='utf-8') as toml_file_link:
                    kwargs[key] = toml_file_link.read().replace('\r\n', '\n')
            except:
                # If we failed, just keep the value
                pass
        elif isinstance(kwargs[key], dict):
            kwargs[key] = _replace_files(kwargs[key], caller_directory)

    return kwargs


def _get_mimetype(filename):
    mimetype = mimetypes.guess_type(filename)
    if mimetype and mimetype[0]:
        return mimetype[0]

    extension = filename.split('.')[-1]

    return mimetype_overrides.get(extension)
