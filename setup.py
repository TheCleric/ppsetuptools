from os import path
import sys

here = path.abspath(path.dirname(__file__))

sys.path.append(path.join(here, 'ppsetuptools'))
import ppsetuptools

ppsetuptools.setup(
    packages=ppsetuptools.find_packages( # type: ignore
        exclude=["tests", "tests.*"]
    ),
)
