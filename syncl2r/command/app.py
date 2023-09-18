import sys
import typer
from ..console import pprint

help_text = r"""
   _____                      __    ___    ____ 
  / ___/ __  __ ____   _____ / /   |__ \  / __ \
  \__ \ / / / // __ \ / ___// /    __/ / / /_/ /
 ___/ // /_/ // / / // /__ / /___ / __/ / _, _/ 
/____/ \__, //_/ /_/ \___//_____//____//_/ |_|  
      /____/                                    
"""

description = """[red]SyncL2R[/] is an [yellow]all-in-one[/] tool for: 
- [yellow]local and remote file synchronization
- one-click deployment
- and multiple functions.
"""


class Helper:
    @property
    def help(self):
        if len(sys.argv) <= 1:
            print(help_text)
            pprint(description)
        return ""


helper = Helper()

app = typer.Typer(name="Syncl2r", no_args_is_help=True, help=helper.help)

__all__ = ["app"]
