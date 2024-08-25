import os
import sys
import pathlib
import typing
from shlex import quote
from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree
from rich.padding import Padding

from syncl2r.console import pprint
from syncl2r.config import FileSyncConfig
from syncl2r.utils.md5 import batch_calc_local_files_md5

MAX_CHILD_NUM = 20


def walk_directory(
    directory: pathlib.Path,
    tree: Tree,
    *,
    escape_func: typing.Callable[[pathlib.Path], bool] | None = None,
    max_child_num: int = MAX_CHILD_NUM,
) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    child_file_num = len(paths)
    for path in paths[:max_child_num]:
        if escape_func and escape_func(path):
            continue
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            tre = Tree(
                f"[bold magenta]:open_file_folder: [link {path.as_uri()}]{escape(path.name)}",
                style=style,
                guide_style=tree.guide_style,
                expanded=tree.expanded,
                highlight=tree.highlight,
            )
            walk_directory(
                path,
                tre,
                escape_func=escape_func,
                max_child_num=int(max_child_num * 3 / 4),
            )
            if len(tre.children) > 0:
                tree.children.append(tre)

        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link {path.as_uri()}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "📄 "
            tree.add(Text(icon) + text_filename)
    if child_file_num > max_child_num:
        tree.add(Text(f"...{child_file_num-max_child_num} files more"))


def get_dir_tree(
    path: str,
    escape_func: typing.Callable[[pathlib.Path], bool] | None = None,
    cfg=None,
) -> Tree:
    path = os.path.abspath(path)
    tree = Tree(
        f":open_file_folder: [link file://{path}]{path}",
        guide_style="bold bright_blue",
    )
    walk_directory(pathlib.Path(path), tree, escape_func=escape_func, max_child_num=40)
    return tree


def show_sync_file_tree(
    syncConfig: FileSyncConfig, *escape_file: typing.Callable[[pathlib.Path], bool]
):
    pprint("[red bold]file tree prepare to sync: ")

    esc_func_list: list[typing.Callable[[pathlib.Path], bool]] = []
    esc_func_list.append(syncConfig.escape_file)
    esc_func_list.extend(escape_file)

    def esc_func(path: pathlib.Path) -> bool:
        return any(func(path) for func in esc_func_list)

    pprint(
        Padding(
            get_dir_tree(syncConfig.root_path, esc_func),
            (0, 0, 0, 0),
        )
    )


def get_file_md5(path: str) -> str | None:
    res = batch_calc_local_files_md5(path)
    return res.get(path, None)


if __name__ == "__main__":
    print(get_file_md5("./readme.md"))
