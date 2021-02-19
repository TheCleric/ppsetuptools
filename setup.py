import sys
from os import path


def main():
    # I don't like this anymore than you likely do, but I can't get it to work any other way
    here = path.abspath(path.dirname(__file__))

    sys.path.append(path.join(here, 'ppsetuptools'))
    import ppsetuptools  # pylint: disable=import-outside-toplevel

    ppsetuptools.setup(
        packages=ppsetuptools.find_packages(
            exclude=["tests", "tests.*"]
        ),
    )


if __name__ == "__main__":
    main()
