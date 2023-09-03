import os
import pathlib
import typing
from console import pprint
from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree
from rich.padding import Padding
from config import FileSyncConfig


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
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue
        if escape_func and escape_func(path):
            continue
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: [link {path.as_uri()}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch, escape_func=escape_func)
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


def show_sync_file_tree(syncConfig: FileSyncConfig):
    pprint("[red bold]file tree prepare to sync: ")
    # TODO 此处应该对比本地和远程文件,将不同的文件进行标注
    pprint(
        Padding(
            get_dir_tree(syncConfig.root_path, syncConfig.escape_file),
            (0, 0, 0, 0),
        )
    )


def get_file_md5(path: str) -> str | None:
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return None
    match os.name:
        case "nt":
            res = os.popen(f"certutil -hashfile {path} md5")
            mds = res.read().split("\n")[1]
            return mds
        case "posix":
            res = os.popen(f"md5sum {path}")
            return res.read()


if __name__ == "__main__":
    print(get_file_md5("./readme.md"))
