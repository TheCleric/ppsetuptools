rm -rf dist \
    && rm -rf build \
    && rm -rf *.egginfo \
    && python setup.py sdist bdist_wheel \
    && pytest -v --doctest-modules --cov=ppsetuptools --cov-report term-missing tests \
    && twine check dist/* \
    && autopep8 --in-place --recursive .
