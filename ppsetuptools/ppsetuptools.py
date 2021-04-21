import inspect
import mimetypes
from os import path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import setuptools
import toml
from setuptools import *  # pylint: disable=function-redefined,redefined-builtin,unused-wildcard-import,wildcard-import

mimetype_overrides: Dict[str, str] = {
    'md': 'text/markdown'
}

valid_setup_params = ['name', 'version', 'description', 'long_description', 'long_description_content_type', 'author',
                      'author_email', 'maintainer', 'maintainer_email', 'url', 'download_url', 'packages',
                      'py_modules', 'scripts', 'ext_package', 'ext_modules', 'classifiers', 'distclass', 'script_name',
                      'script_args', 'options', 'license', 'license_files', 'keywords', 'platforms', 'cmdclass',
                      'package_dir', 'include_package_data', 'exclude_package_data', 'package_data', 'zip_safe',
                      'install_requires', 'entry_points', 'extras_require', 'python_requires', 'namespace_packages',
                      'test_suite', 'tests_require', 'test_loader', 'eager_resources', 'use_2to3',
                      'convert_2to3_doctests', 'use_2to3_fixers', 'use_2to3_exclude_fixers', 'project_urls']

__all__ = setuptools.__all__

_SETUPTOOLS_OUTPUT_PARAMS = Union[str, Tuple[str, str]]  # pylint: disable=invalid-name
_SETUPTOOLS_OUTPUT_BASE_TYPES = Optional[Union[str, Dict[str, Any], List[str]]]  # pylint: disable=invalid-name
_SETUPTOOLS_OUTPUT_TYPES = Union[  # pylint: disable=invalid-name
    _SETUPTOOLS_OUTPUT_BASE_TYPES,
    Tuple[_SETUPTOOLS_OUTPUT_BASE_TYPES, _SETUPTOOLS_OUTPUT_BASE_TYPES]
]
_SETUPTOOLS_TRANSFORM_FUNCTION = Callable[..., _SETUPTOOLS_OUTPUT_TYPES]  # pylint: disable=invalid-name


def _no_transform(value: _SETUPTOOLS_OUTPUT_TYPES) -> _SETUPTOOLS_OUTPUT_TYPES:
    return value


def _contributor_transform(contributors: List[Dict[str, str]]) -> Tuple[Optional[str], Optional[str]]:
    contributor_names = []
    contributor_emails = []
    if contributors and isinstance(contributors, list):
        for contributor in contributors:
            if isinstance(contributor, dict):
                name = contributor.get('name')
                email = contributor.get('email')
                if name and email:
                    contributor_names.append('{} <{}>'.format(name, email))
                elif name:
                    contributor_names.append(name)
                elif email:
                    contributor_emails.append(email)
    return (','.join(contributor_names) or None, ','.join(contributor_emails) or None)


def _join_list_transform(value: List[str]) -> Optional[str]:
    if not value:
        return None

    return ','.join(value)


def _license_transform(license_value: Union[str, Dict[str, str]]) -> Tuple[Optional[str], Optional[List[str]]]:
    if not license_value:
        return (None, None)

    if isinstance(license_value, str):
        license_file = None
        license_text: Optional[str] = license_value
    elif isinstance(license_value, dict):
        license_file = license_value.get('file')
        license_text = license_value.get('text')
    else:
        raise ValueError(
            "Expected pyproject.toml value for project.license to be a dictionary. Got {}".format(type(license_value)))
    if license_file and license_text:
        raise ValueError(
            'project.license should contain either file or text, not both.')

    if license_file:
        return (None, [license_file])

    return (license_text, None)


def _readme_transform(readme_value: str, caller_directory: str) -> Tuple[Optional[str], Optional[str]]:
    if not readme_value:
        return (readme_value, None)

    long_description = _replace_file(readme_value, caller_directory)
    long_description_content_type = _get_mimetype(readme_value)

    return long_description, long_description_content_type


_pyproject_setuptools_mapping: Dict[str, Tuple[_SETUPTOOLS_OUTPUT_PARAMS, _SETUPTOOLS_TRANSFORM_FUNCTION]] = {
    'readme': (('long_description', 'long_description_content_type'), _readme_transform),
    'requires-python': ('python_requires', _no_transform),
    'license': (('license', 'license_files'), _license_transform),
    'authors': (('author', 'author_email'), _contributor_transform),
    'maintainers': (('maintainer', 'maintainer_email'), _contributor_transform),
    'keywords': ('keywords', _join_list_transform),
    'urls': ('project_urls', _no_transform),
    'entry-points': ('entry_points', _no_transform),
    'dependencies': ('install_requires', _no_transform),
    'optional-dependencies': ('extras_require', _no_transform),
}


def setup(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:  # pylint: disable=function-redefined
    try:
        caller_directory = path.abspath(path.dirname(inspect.stack()[1].filename))
    except:  # pylint: disable=bare-except
        caller_directory = '.'

    with open(path.join(caller_directory, 'pyproject.toml'), 'r') as pptoml:
        pyproject_toml: Union[str, bytes] = pptoml.read()
        if isinstance(pyproject_toml, bytes):  # pragma: no cover
            pyproject_toml = pyproject_toml.decode('utf-8')

    pyproject_data = toml.loads(pyproject_toml)

    parsed_kwargs = _parse_kwargs(pyproject_data['project'], caller_directory)
    parsed_kwargs.update(kwargs)

    print('Calling setuptools.setup with args:\n', args)
    print('And kwargs:\n', parsed_kwargs)

    return setuptools.setup(*args, **parsed_kwargs)


def _filter_dict(kwargs: Dict[str, Any], allowed_params: List[str]) -> Dict[str, Any]:
    return {k: v for k, v in kwargs.items() if k in allowed_params}


def _parse_kwargs(kwargs: Dict[str, Any], caller_directory: str) -> Dict[str, Any]:
    # Pre-include actual setuptools kwargs like name, which does not need to be transformed
    kwargs_parsed: Dict[str, Any] = _filter_dict(kwargs, valid_setup_params)

    for key, (output_keys, transform_func) in _pyproject_setuptools_mapping.items():
        value = kwargs.get(key)
        transform_signature = inspect.signature(transform_func)
        if 'caller_directory' in transform_signature.parameters.keys():
            result = transform_func(value, caller_directory)  # pylint: disable=not-callable
        else:
            result = transform_func(value)  # pylint: disable=not-callable
        if isinstance(output_keys, tuple):
            if not isinstance(result, tuple) or len(result) != len(output_keys):
                raise ValueError('Expected {} values to return from {} , but received {}'.format(  # pragma: no cover
                    len(output_keys),
                    transform_func.__name__,  # pylint: disable=no-member
                    len(result) if isinstance(result, tuple) else 1)
                )
            for index, output_key in enumerate(output_keys):
                kwargs_parsed[output_key] = result[index]
        else:
            kwargs_parsed[output_keys] = result

    return kwargs_parsed


def _replace_file(filename: str, caller_directory: str) -> str:
    with open(path.join(caller_directory, filename), 'r', encoding='utf-8') as file_link:
        file_data: Union[str, bytes] = file_link.read()
        if isinstance(file_data, bytes):
            file_data = file_data.decode('utf-8')  # pragma: no cover
        return file_data.replace('\r\n', '\n')


def _get_mimetype(filename: str) -> Optional[str]:
    mimetype = mimetypes.guess_type(filename.lower())
    if mimetype and mimetype[0]:
        return mimetype[0]

    extension = filename.split('.')[-1].lower()

    return mimetype_overrides.get(extension)
