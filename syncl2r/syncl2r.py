import typer

from .command import app


__all__ = ["main"]


def main():
    app()


if __name__ == "__main__":
    main()
