# pylint:disable = unused-wildcard-import
import codecs
import inspect
import mimetypes
from os import path

import setuptools  # type: ignore
import toml
from setuptools import *  # pylint: disable=function-redefined,redefined-builtin,unused-wildcard-import,wildcard-import

# pylint: disable = function-redefined
mimetype_overrides = {
    'md': 'text/markdown'
}

valid_setup_params = ['name', 'version', 'description', 'long_description', 'long_description_content_type', 'url',
                      'author', 'author_email', 'maintainer', 'maintainer_email', 'license', 'classifiers', 'keywords',
                      'install_requires', 'include_package_data', 'extras_require', 'zip_safe', 'packages', 'scripts',
                      'package_data', 'data_files', 'entry_points']

open = codecs.open  # pylint:disable=redefined-builtin


def setup(*args, **kwargs):
    caller_directory = '.'

    try:
        caller_directory = path.abspath(path.dirname(inspect.stack()[1].filename))
    except:  # pylint: disable=bare-except
        pass

    with open(path.join(caller_directory, 'pyproject.toml'), 'r', encoding='utf-8') as pptoml:
        pyproject_toml = pptoml.read()

    pyproject_data = toml.loads(pyproject_toml)

    # Treat dependencies as install_requires
    dependencies = pyproject_data["project"].get("dependencies")
    if dependencies:
        install_requires = pyproject_data["project"].get("install_requires", [])
        pyproject_data["project"]["install_requires"] = list(set(install_requires + dependencies))

    # Treat optional-dependencies as extra_requires
    optionals = pyproject_data["project"].get("optional-dependencies")
    if optionals:
        extras = pyproject_data["project"].get("extras_require", {})
        optionals.update(extras)
        pyproject_data["project"]["extras_require"] = optionals

    kwargs_copy = kwargs.copy()
    kwargs_copy.update(_filter_dict(pyproject_data['project'], valid_setup_params))

    kwargs = _parse_kwargs(kwargs_copy, caller_directory)

    print('Calling setuptools.setup with args: {}'.format(args))
    print('And kwargs:')
    print(kwargs)

    return setuptools.setup(*args, **kwargs)


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
            except:  # pylint: disable=bare-except
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
