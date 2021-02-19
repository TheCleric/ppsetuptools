import builtins
import inspect
from os import path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import toml

import ppsetuptools.ppsetuptools as ppsetuptools  # pylint: disable = import-error

_DATA_DIR = 'data'
_HERE = path.abspath(path.dirname(__file__))


def thrower(*args, **kwargs):
    raise Exception("")


def test_setup():
    with open(path.join(_HERE, _DATA_DIR, 'test_pyproject.toml'), 'r') as test_toml_file:
        test_toml_file_contents = test_toml_file.read()

    test_toml_data = toml.loads(test_toml_file_contents)

    test_toml_data['project']['install_requires'] = list(
        set(
            test_toml_data['project']['install_requires'] + test_toml_data['project']['dependencies']
        )
    )

    test_toml_data['project']['optional-dependencies'].update(test_toml_data['project']['extras_require'])
    test_toml_data['project']['extras_require'] = test_toml_data['project']['optional-dependencies']

    mo = mock_open(read_data=test_toml_file_contents.encode('utf-8'))
    setup_mock = MagicMock()

    with patch('ppsetuptools.setuptools.setup', setup_mock):
        with patch('builtins.open', mo):
            ppsetuptools.setup()

    assert mo.call_count == 1
    setup_mock.assert_called_once_with(
        **ppsetuptools._filter_dict(test_toml_data['project'], ppsetuptools.valid_setup_params)
    )


def test_setup_inspect_stack_error():
    with open(path.join(_HERE, _DATA_DIR, 'test_pyproject.toml'), 'r') as test_toml_file:
        test_toml_file_contents = test_toml_file.read()

    test_toml_data = toml.loads(test_toml_file_contents)

    mo = mock_open(read_data=test_toml_file_contents.encode('utf-8'))
    setup_mock = MagicMock()

    with patch('inspect.stack', thrower):
        with patch('ppsetuptools.setuptools.setup', setup_mock):
            with patch('builtins.open', mo):
                ppsetuptools.setup()

    assert mo.call_count == 1
    assert setup_mock.call_count == 1


def test_replace_files():
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
    }

    with open(path.join(_HERE, _DATA_DIR, test_filename), 'r', encoding='utf-8') as test_file:
        test_file_contents = test_file.read()

    result = ppsetuptools._replace_files(test_toml_dict, _HERE)

    assert result['long_description'].strip() == test_file_contents.strip()


def test_replace_files_deep():
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'options': {
            'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
        }
    }

    with open(path.join(_HERE, _DATA_DIR, test_filename), 'r', encoding='utf-8') as test_file:
        test_file_contents = test_file.read()

    result = ppsetuptools._replace_files(test_toml_dict, _HERE)

    assert result['options']['long_description'].strip() == test_file_contents.strip()


def test_replace_files_file_error():
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'long_description': 'file: ' + test_filename
    }

    with patch('ppsetuptools.open', thrower):
        result = ppsetuptools._replace_files(test_toml_dict, _HERE)

    assert result['long_description'] == 'file: ' + test_filename


def test_parse_kwargs():
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
    }

    here = path.abspath(path.dirname(__file__))

    test_file_content_type = ppsetuptools._get_mimetype(test_filename)

    result = ppsetuptools._parse_kwargs(test_toml_dict, here)

    assert not result['long_description'].startswith('file:')
    assert result['long_description_content_type'] == test_file_content_type


def test_get_mimetype_markdown():
    test_filename = 'test_readme.md'
    test_file_content_type = ppsetuptools._get_mimetype(test_filename)
    assert test_file_content_type == 'text/markdown'


def test_get_mimetype_supported_mimetypes():
    test_filename = 'test.json'
    test_file_content_type = ppsetuptools._get_mimetype(test_filename)
    assert test_file_content_type == 'application/json'
