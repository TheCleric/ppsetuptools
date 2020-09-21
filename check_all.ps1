Remove-Item -Recurse -Force -Confirm:$false dist `
    || Remove-Item -Recurse -Force -Confirm:$false build `
    || Remove-Item -Recurse -Force -Confirm:$false *.egginfo `
    || pre-commit install `
    && python setup.py sdist bdist_wheel `
    && pytest tests --doctest-modules --cov=ppsetuptools `
    && twine check dist/*
