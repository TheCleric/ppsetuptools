rm -rf dist \
    && rm -rf build \
    && rm -rf *.egginfo \
    && python setup.py sdist bdist_wheel \
    && pytest --doctest-modules --cov=ppsetuptools --cov-report term-missing tests \
    && twine check dist/* \
    && autopep8 --in-place --recursive .
