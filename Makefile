REQUIRE_PIP  := true
PACKAGE_NAME := ppsetuptools
TESTS_DIR := tests

autopep8:
	autopep8 --in-place --recursive *.py $(PACKAGE_NAME) $(TESTS_DIR)

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egginfo

build-review: isort autopep8 lint coverage twine-check test-github-actions

coverage:
	pytest -v --doctest-modules --cov=$(PACKAGE_NAME) --cov-fail-under=100 --cov-report term-missing --cov-report html $(TESTS_DIR)

install: upgrade-pip
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) pip install -e .

install-dev: upgrade-pip
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) pip install -e .[dev,test]

install-test: upgrade-pip
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) pip install -e .[test]

isort:
	isort *.py $(PACKAGE_NAME)/ $(TESTS_DIR)/

lint: pylint mypy

mypy:
	python3 -m mypy *.py $(PACKAGE_NAME)/ $(TESTS_DIR)/ --namespace-packages

pylint:
	# Lint all files outside of any virtual environment
	find . -type f -name "*.py" | grep -v venv | grep -v build | xargs python3 -m pylint

setup: clean upgrade-pip
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) pip install setuptools wheel twine toml
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) pip install setuptools --upgrade
	python setup.py sdist bdist_wheel

twine-check: setup
	twine check dist/*

twine-upload: twine-check
	twine upload dist/*

upgrade-pip:
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) pip install --disable-pip-version-check upgrade-ensurepip
	PIP_REQUIRE_VIRTUALENV=$(REQUIRE_PIP) python -m upgrade_ensurepip

ACT_EXISTS := $(shell act --help 2> /dev/null)

ifeq ($(ACT_EXISTS),)
test-github-actions:
	@echo "Testing GitHub actions requires act to be installed. See: https://github.com/nektos/act"
	exit 1
else
test-github-actions:
	act pull_request -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 $(ACT_FLAGS)
endif
