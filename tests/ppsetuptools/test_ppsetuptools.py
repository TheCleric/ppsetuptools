import mimetypes
from os import path
from unittest.mock import MagicMock, patch, mock_open
import builtins
import setuptools
import toml

import ppsetuptools.ppsetuptools as ppsetuptools  # pylint: disable = import-error

_DATA_DIR = 'data'
_HERE = path.abspath(path.dirname(__file__))


def test_setup():
    old_setuptools_setup = ppsetuptools.setuptools_setup
    
    try:
        with open(path.join(_HERE, _DATA_DIR, 'test_pyproject.toml'), 'r') as test_toml_file:
            test_toml_file_contents = test_toml_file.read()

        test_toml_data = toml.loads(test_toml_file_contents)

        setup_mock = MagicMock()
        mo = mock_open(read_data=test_toml_file_contents.encode('utf-8'))
        ppsetuptools.setuptools_setup = setup_mock
        with patch('builtins.open', mo):
            ppsetuptools.setup()
        ppsetuptools.setuptools_setup = old_setuptools_setup
    except Exception as ex:
        ppsetuptools.setuptools_setup = old_setuptools_setup
        raise(ex)

    mo.assert_called_once()
    setup_mock.assert_called_once_with(**test_toml_data['project'])


def test_replace_files():
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'project': {
            'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
        }
    }

    with open(path.join(_HERE, _DATA_DIR, test_filename), 'r', encoding='utf-8') as test_file:
        test_file_contents = test_file.read()

    result = ppsetuptools._replace_files(test_toml_dict, _HERE)

    assert result['project']['long_description'].strip() == test_file_contents.strip()


def test_parse_kwargs():
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'project': {
            'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
        }
    }

    here = path.abspath(path.dirname(__file__))

    test_file_content_type = mimetypes.guess_type(test_filename)

    result = ppsetuptools._parse_kwargs(test_toml_dict, here)

    assert not result['project']['long_description'].startswith('file:')
    assert result['project']['long_description_content_type'] == test_file_content_type
