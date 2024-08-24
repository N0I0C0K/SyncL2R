import os
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


def walk_directory(
    directory: pathlib.Path,
    tree: Tree,
    *,
    escape_func: typing.Callable[[pathlib.Path], bool] | None = None,
) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.name.lower()),
    )
    for path in paths:
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
            walk_directory(path, tre, escape_func=escape_func)
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


def get_dir_tree(
    path: str, escape_func: typing.Callable[[pathlib.Path], bool] | None = None
) -> Tree:
    path = os.path.abspath(path)
    tree = Tree(
        f":open_file_folder: [link file://{path}]{path}",
        guide_style="bold bright_blue",
    )
    walk_directory(pathlib.Path(path), tree, escape_func=escape_func)
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
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return None
    match os.name:
        case "nt":
            res = os.popen(f'certutil -hashfile "{path}" md5')
            mds = res.read().split("\n")[1]
            return mds
        case "posix":
            res = os.popen(f"md5sum {quote(path)}")
            return res.read()


if __name__ == "__main__":
    print(get_file_md5("./readme.md"))
