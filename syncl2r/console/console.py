from rich.style import Style
from rich.theme import Theme
from rich.console import Console

cus_theme = Theme({
    'info': 'green',
    'info.low': 'dim cyan on black',
    'warning': 'bold yellow',
    'danger.high': 'bold reverse red',
    'danger': 'bold red',
    'path': 'yellow3'
})

console: Console = Console(theme=cus_theme)

pprint = console.print
llog = console.log

__all__ = ['console', 'pprint']
