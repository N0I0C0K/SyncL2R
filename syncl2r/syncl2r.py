import typer

from .config import load_config
from .console import pprint
from .command import app


@app.command()
def test():
    config = load_config()
    pprint(config)


__all__ = ["main"]


def main():
    app()


if __name__ == "__main__":
    main()
