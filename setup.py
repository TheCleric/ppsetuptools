from os import path
import sys


def main():
    # I don't like this anymore than you likely do, but I can't get it to work any other way
    here = path.abspath(path.dirname(__file__))

    sys.path.append(path.join(here, 'ppsetuptools'))
    import ppsetuptools

    ppsetuptools.setup(
        packages=ppsetuptools.find_packages(  # type: ignore
            exclude=["tests", "tests.*"]
        ),
    )


if __name__ == "__main__":
    main()
