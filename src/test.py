from console import console
from utils import utils
from rich import columns

console.print(columns.Columns(
    [utils.get_dir_tree('./test'), utils.get_dir_tree('./src')]))
