Remove-Item -Recurse -Force -Confirm:$false dist `
    || Remove-Item -Recurse -Force -Confirm:$false build `
    || Remove-Item -Recurse -Force -Confirm:$false *.egginfo `
    || pre-commit install `
    && python setup.py sdist bdist_wheel `
    && pytest --doctest-modules --cov=ppsetuptools --cov-report term-missing tests `
    && twine check dist/* `
    && autopep8 --in-place --recursive .
