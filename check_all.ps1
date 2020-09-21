Remove-Item -Recurse -Force -Confirm:$false dist `
    && Remove-Item -Recurse -Force -Confirm:$false build `
    && Remove-Item -Recurse -Force -Confirm:$false *.egginfo `
    && pytest tests --doctest-modules --cov=ppsetuptools `
    && python setup.py sdist bdist_wheel `
    && twine check dist/* `
    && pre-commit install
