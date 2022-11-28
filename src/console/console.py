from rich.style import Style
from rich.theme import Theme
from rich.console import Console

theme = Theme({
    "info": "cyan",
    "warning": "magenta",
    "danger": "bold red"
})

console: Console = Console(theme=theme)

cpprint = console.print

__all__ = ['console', 'cpprint']
