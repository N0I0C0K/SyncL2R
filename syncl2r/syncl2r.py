from syncl2r.config import load_config

from .command import app


__all__ = ["main"]


def main():
    try:
        load_config()
    except:
        pass
    app()


if __name__ == "__main__":
    main()
