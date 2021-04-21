import copy
from os import path
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock, mock_open, patch

import pytest
import toml

import ppsetuptools.ppsetuptools as ppsetuptools
from ppsetuptools.ppsetuptools import mimetype_overrides

_DATA_DIR = 'data'
_HERE = path.abspath(path.dirname(__file__))


@pytest.fixture(name='thrower')
def _thrower() -> MagicMock:
    return MagicMock(side_effect=Exception)


def test_setup() -> None:
    with open(path.join(_HERE, _DATA_DIR, 'test_pyproject.toml'), 'r') as test_toml_file:
        test_toml_file_contents = test_toml_file.read()

    with open(path.join(_HERE, _DATA_DIR, 'test_readme.md'), 'r') as test_readme_file:
        readme_contents = test_readme_file.read()

    test_toml_data = toml.loads(test_toml_file_contents)

    _mock_open = MagicMock(side_effect=[
        mock_open(read_data=test_toml_file_contents)(),
        mock_open(read_data=readme_contents)(),
    ])

    test_toml_data_copy = copy.copy(test_toml_data)
    test_toml_data['project']['readme'] = path.join(_HERE, _DATA_DIR, test_toml_data['project']['readme'])

    expected_params = ppsetuptools._filter_dict(  # pylint: disable=protected-access
        ppsetuptools._parse_kwargs(  # pylint: disable=protected-access
            test_toml_data_copy['project'],
            path.join(_HERE, _DATA_DIR)
        ),
        ppsetuptools.valid_setup_params
    )

    with patch('setuptools.setup', MagicMock()) as setup_mock, \
            patch('ppsetuptools.ppsetuptools.open', _mock_open):
        ppsetuptools.setup()
        assert _mock_open.call_count == 2

        setup_mock.assert_called_once_with(
            **expected_params
        )


def test_setup_inspect_stack_error(thrower: Callable[..., Any]) -> None:
    with open(path.join(_HERE, _DATA_DIR, 'test_pyproject.toml'), 'r') as test_toml_file:
        test_toml_file_contents = test_toml_file.read()

    with open(path.join(_HERE, _DATA_DIR, 'test_readme.md'), 'r') as test_readme_file:
        readme_contents = test_readme_file.read()

    assert toml.loads(test_toml_file_contents) is not None

    _mock_open = MagicMock(side_effect=[
        mock_open(read_data=test_toml_file_contents)(),
        mock_open(read_data=readme_contents)(),
    ])

    with patch('inspect.stack', thrower), \
            patch('setuptools.setup', MagicMock()) as setup_mock, \
            patch('builtins.open', _mock_open):
        ppsetuptools.setup()
        assert _mock_open.call_count == 2
        setup_mock.assert_called_once()


def test_replace_file() -> None:
    test_filename = path.join(_DATA_DIR, 'test_readme.md')

    with open(path.join(_HERE, test_filename), 'r', encoding='utf-8') as test_file:
        test_file_contents = test_file.read()

    result = ppsetuptools._replace_file(test_filename, _HERE)  # pylint: disable=protected-access

    assert result == test_file_contents


def test_replace_file_file_error(thrower: Callable[..., Any]) -> None:
    test_filename = path.join(_DATA_DIR, 'test_readme.md')

    with pytest.raises(Exception), patch('builtins.open', thrower):
        ppsetuptools._replace_file(test_filename, _HERE)  # pylint: disable=protected-access


def test_parse_kwargs() -> None:
    test_filename = 'test_readme.md'
    test_toml_dict: Dict[str, Any] = {
        'readme': path.join(_DATA_DIR, test_filename),
        'authors': [{
            'name': 'Me',
            'email': 'me@me.com'
        }],
        'maintainers': [{
            'name': 'Me2',
            'email': 'me2@me.com'
        }]
    }

    test_file_content_type = ppsetuptools._get_mimetype(test_filename)  # pylint: disable=protected-access

    with patch('inspect.stack', MagicMock(return_value=[{}, {'filename': path.join(_HERE, 'setup.py')}])):
        result = ppsetuptools._parse_kwargs(  # pylint: disable=protected-access
            test_toml_dict,
            _HERE
        )

    assert result['long_description'] == ppsetuptools._replace_file(  # pylint: disable=protected-access
        path.join(_DATA_DIR, test_filename),
        _HERE
    )
    assert result['long_description_content_type'] == test_file_content_type
    assert result['author'] == test_toml_dict['authors'][0]['name'] + " <" + test_toml_dict['authors'][0]['email'] + ">"
    assert result['maintainer'] == test_toml_dict['maintainers'][0]['name'] + \
        " <" + test_toml_dict['maintainers'][0]['email'] + ">"


def test_contributor_transform() -> None:
    authors = [
        {
            'name': 'Me',
            'email': 'me@me.com'
        }
    ]
    author, author_email = ppsetuptools._contributor_transform(authors)  # pylint: disable=protected-access
    assert author == 'Me <me@me.com>'
    assert author_email is None


def test_contributor_transform_no_name() -> None:
    authors = [
        {
            'email': 'me@me.com'
        }
    ]
    author, author_email = ppsetuptools._contributor_transform(authors)  # pylint: disable=protected-access
    assert author is None
    assert author_email == 'me@me.com'


def test_contributor_transform_no_email() -> None:
    authors = [
        {
            'name': 'Me',
        }
    ]
    author, author_email = ppsetuptools._contributor_transform(authors)  # pylint: disable=protected-access
    assert author == 'Me'
    assert author_email is None


def test_contributor_transform_no_data() -> None:
    authors: List[Dict[str, str]] = [
        {
        }
    ]
    author, author_email = ppsetuptools._contributor_transform(authors)  # pylint: disable=protected-access
    assert author is None
    assert author_email is None


def test_license_transform_file() -> None:
    license_data = {
        'file': 'license.txt'
    }
    license_text, license_files = ppsetuptools._license_transform(license_data)  # pylint: disable=protected-access
    assert license_text is None
    assert license_files == ['license.txt']


def test_license_transform_text() -> None:
    license_data = {
        'text': 'LGPL'
    }
    license_text, license_files = ppsetuptools._license_transform(license_data)  # pylint: disable=protected-access
    assert license_text == 'LGPL'
    assert license_files is None


def test_license_transform_both() -> None:
    license_data = {
        'text': 'LGPL',
        'file': 'license.txt'
    }
    with pytest.raises(ValueError):
        ppsetuptools._license_transform(license_data)  # pylint: disable=protected-access


def test_license_transform_old_style() -> None:
    license_data = 'LGPL'

    license_text, license_files = ppsetuptools._license_transform(license_data)  # pylint: disable=protected-access
    assert license_text == 'LGPL'
    assert license_files is None


def test_license_transform_invalid() -> None:
    license_data: List[Any] = [None]

    with pytest.raises(ValueError):
        ppsetuptools._license_transform(license_data)  # type: ignore # pylint: disable=protected-access


def test_readme_transform() -> None:
    readme = path.join(_HERE, _DATA_DIR, 'test_readme.md')
    with open(readme) as readme_file:
        readme_data = readme_file.read()

    long_description, long_description_content_type = ppsetuptools._readme_transform(  # pylint: disable=protected-access
        readme,
        path.join(_HERE, _DATA_DIR)
    )
    assert long_description == readme_data
    assert long_description_content_type == 'text/markdown'


def test_readme_transform_none() -> None:
    long_description, long_description_content_type = ppsetuptools._readme_transform(  # pylint: disable=protected-access
        None,  # type: ignore[arg-type]
        path.join(_HERE, _DATA_DIR)
    )
    assert long_description is None
    assert long_description_content_type is None


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
