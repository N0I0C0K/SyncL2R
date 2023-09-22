from syncl2r.config import load_config

from .command import app


__all__ = ["main"]


def main():
    load_config()
    app()


if __name__ == "__main__":
    main()
