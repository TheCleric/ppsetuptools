# ppsetuptools => pyproject setuptools

A drop in replacement for python setuptools that uses pyproject.toml files
for python 3.5+ projects

## Usage

To install run `pip install ppsetuptools` in your project.

Place your project settings in the `[project]` table of your pyproject.toml.
Also ensure that `ppsetuptools` is included in your `[build-system]` table
in the `requires` list.

Replace setuptools import in your `setup.py` with an import of ppsetuptools.
ppsetuptools exposes all functions from setuptools, and in addition will map
your `pyproject.toml` data to the call to `setuptools.setup` for you.

### Example `pyproject.toml`

```toml
[project]
name = 'my_package'
project_name = 'my_package'
version = '1.0.0'
long_description = 'file: README.md'
install_requires = [
    'setuptools',
    'toml'
]
include_package_data = true

[build-system]
requires = [
    'setuptools >= 40.8.0',
    'wheel >= 0.35.1',
    'toml >= 0.10.1'
]
build-backend = 'setuptools.build_meta'
```

### Example `setup.py`

```python
from ppsetuptools import setup

setup()
```

### File references

ppsetuptools will attempt to replace any strings beginning with "file:" with the
file's contents. For the long_description entry, ppsetuptools will also attempt
to fill long_description_content_type for you based on the filename.

### File locations

As of now, the library attempts to find a `pyproject.toml` file in the same
directory as the python file that called it. So if calling directly from
`setup.py`, ensure that your `pyproject.toml` file is in the same directory.

As well any file references will attempt to be followed from this location.
E.g., if including a `file: README.md` reference, ppsetuptools will look for
`README.md` in the same directory as the file that called it.

### Function support

As of now, ppsetuptools does not support calculated values within the
`pyproject.toml` file. If calculated values are needed, ppsetuptools
will combine the args passed to the `setup` call with the values in the
`pyproject.toml` file, so you may call setup like so, and it will still use your
`pyproject.toml` values in addition to the passed values.

```python
from ppsetuptools import setup, find_packages

setup(
    find_packages(exclude=['tests'])
)
```

## PEP 621

NOTE: This is not currently PEP 621 as that PEP is still in draft status. This
project will be made PEP 621 compliant in the future if the PEP is accepted.
