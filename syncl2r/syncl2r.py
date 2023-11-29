from syncl2r.config import load_config

from .command import app
from .console import pprint

__all__ = ["main"]


def main():
    try:
        load_config()
    except Exception as e:
        pprint(f"Some error happened, detail: {e}")
    app()


if __name__ == "__main__":
    main()
