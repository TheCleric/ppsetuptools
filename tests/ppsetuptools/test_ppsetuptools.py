from os import path
from typing import Any, Dict, List
from unittest.mock import MagicMock, mock_open, patch

import toml

import ppsetuptools.ppsetuptools as ppsetuptools
from ppsetuptools.ppsetuptools import mimetype_overrides

_DATA_DIR = 'data'
_HERE = path.abspath(path.dirname(__file__))


def thrower(*args: List[Any], **kwargs: Dict[str, Any]) -> None:
    raise Exception("")


def test_setup() -> None:
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

    with patch('setuptools.setup', MagicMock()) as setup_mock, \
            patch('builtins.open', mock_open(read_data=test_toml_file_contents.encode('utf-8'))) as _mock_open:
        ppsetuptools.setup()
        _mock_open.assert_called_once()

        setup_mock.assert_called_once_with(
            **ppsetuptools._filter_dict(test_toml_data['project'], ppsetuptools.valid_setup_params)  # pylint: disable=protected-access
        )


def test_setup_inspect_stack_error() -> None:
    with open(path.join(_HERE, _DATA_DIR, 'test_pyproject.toml'), 'r') as test_toml_file:
        test_toml_file_contents = test_toml_file.read()

    assert toml.loads(test_toml_file_contents) is not None

    with patch('inspect.stack', thrower), \
            patch('setuptools.setup', MagicMock()) as setup_mock, \
            patch('builtins.open', mock_open(read_data=test_toml_file_contents.encode('utf-8'))) as _mock_open:
        ppsetuptools.setup()
        _mock_open.assert_called_once()
        setup_mock.assert_called_once()


def test_replace_files() -> None:
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
    }

    with open(path.join(_HERE, _DATA_DIR, test_filename), 'r', encoding='utf-8') as test_file:
        test_file_contents = test_file.read()

    result = ppsetuptools._replace_files(test_toml_dict, _HERE)  # pylint: disable=protected-access

    assert result['long_description'].strip() == test_file_contents.strip()


def test_replace_files_deep() -> None:
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'options': {
            'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
        }
    }

    with open(path.join(_HERE, _DATA_DIR, test_filename), 'r', encoding='utf-8') as test_file:
        test_file_contents = test_file.read()

    result = ppsetuptools._replace_files(test_toml_dict, _HERE)  # pylint: disable=protected-access

    assert result['options']['long_description'].strip() == test_file_contents.strip()


def test_replace_files_file_error() -> None:
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'long_description': 'file: ' + test_filename
    }

    with patch('ppsetuptools.open', thrower):
        result = ppsetuptools._replace_files(test_toml_dict, _HERE)  # pylint: disable=protected-access

    assert result['long_description'] == 'file: ' + test_filename


def test_parse_kwargs() -> None:
    test_filename = 'test_readme.md'
    test_toml_dict = {
        'long_description': 'file: ' + path.join(_DATA_DIR, test_filename)
    }

    here = path.abspath(path.dirname(__file__))

    test_file_content_type = ppsetuptools._get_mimetype(test_filename)  # pylint: disable=protected-access

    result = ppsetuptools._parse_kwargs(test_toml_dict, here)  # pylint: disable=protected-access

    assert not result['long_description'].startswith('file:')
    assert result['long_description_content_type'] == test_file_content_type


def test_get_mimetype_markdown() -> None:
    test_filename = 'test_readme.md'
    test_file_content_type = ppsetuptools._get_mimetype(test_filename)  # pylint: disable=protected-access
    assert test_file_content_type == 'text/markdown'


def test_get_mimetype_supported_mimetypes() -> None:
    test_filename = 'test.json'
    test_file_content_type = ppsetuptools._get_mimetype(test_filename)  # pylint: disable=protected-access
    assert test_file_content_type == 'application/json'


def test_get_mimetype_unsupported_mimetypes() -> None:
    with patch.dict(mimetype_overrides, {'blah': 'text/blah'}):
        test_filename = 'test.blah'
        test_file_content_type = ppsetuptools._get_mimetype(test_filename)  # pylint: disable=protected-access
        assert test_file_content_type == 'text/blah'
