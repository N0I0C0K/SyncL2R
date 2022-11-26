import os
import pathlib

from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree


def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
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
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: {escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link {path.as_uri()}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "📄 "
            tree.add(Text(icon) + text_filename)


def get_dir_tree(path: str) -> Tree:
    path = os.path.abspath(path)
    tree = Tree(
        f":open_file_folder: [link file://{path}]{path}",
        guide_style="bold bright_blue",
    )
    walk_directory(pathlib.Path(path), tree)
    return tree
