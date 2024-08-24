import os
import enum
import paramiko
import typing
import pathlib

from shlex import quote
from .utils import get_file_md5
from rich.tree import Tree
from rich.text import Text
from rich.filesize import decimal


class FileType(enum.IntFlag):
    DIR = 4
    NORMAL_FILE = 8


def upload_file_or_dir(
    sftp_client: paramiko.SFTPClient,
    localfile: str,
    remote_path: str,
    call_back: typing.Callable[[str], None] | None = None,
    *,
    escape_func: typing.Callable[[pathlib.Path], bool] | None = None,
):
    if escape_func and escape_func(pathlib.Path(localfile)):
        return
    if os.path.isdir(localfile):
        upload_dir(sftp_client, localfile, remote_path)
    else:
        upload_file(sftp_client, localfile, remote_path)
        if call_back:
            call_back(localfile)


def upload_dir(sftp_client: paramiko.SFTPClient, localdir: str, remotedir: str):
    if not os.path.isdir(localdir):
        return
    dir_name = os.path.basename(localdir)
    remotedir = f"{remotedir}/{dir_name}"
    if not exist_remote(remotedir, sftp_client):
        sftp_client.mkdir(remotedir)
    for i in os.listdir(localdir):
        upload_file_or_dir(sftp_client, f"{localdir}/{i}", remotedir)


def upload_file(sftp_client: paramiko.SFTPClient, localfile: str, remotedir: str):
    if os.path.isdir(localfile):
        return
    sftp_client.put(localfile, f"{remotedir}/{os.path.basename(localfile)}")


def get_file_type(file_stat: paramiko.SFTPAttributes) -> FileType | None:
    file_mode = file_stat.st_mode >> 12  # type: ignore
    for name in FileType:
        if (file_mode ^ name.value) == 0:
            return name
    return


def get_remote_file_md5(file_path: str, ssh_client: paramiko.SSHClient) -> str:
    stdin, stdout, stderr = ssh_client.exec_command(f"md5sum {quote(file_path)}")
    res = stdout.read().decode().split()
    if len(res) > 0:
        return res[0]
    else:
        return ""


def get_file_type_from_path(
    file_path: str, sftp_client: paramiko.SFTPClient
) -> FileType | None:
    try:
        stat = sftp_client.stat(file_path)
        return get_file_type(stat)
    except:
        return None


def rfile_equal_lfile(
    remote_file_path: str, local_file_path: str, ssh_client: paramiko.SSHClient
) -> bool:
    return get_file_md5(local_file_path) == get_remote_file_md5(
        remote_file_path, ssh_client
    )


def exist_remote(file_path: str, sftp_client: paramiko.SFTPClient) -> bool:
    try:
        sftp_client.stat(file_path)
    except FileNotFoundError:
        return False
    else:
        return True


def show_remote_file_tree(path: str, sftp: paramiko.SFTPClient):
    from syncl2r.console import pprint
    from rich.padding import Padding

    pprint(
        Padding(
            get_remote_file_tree(path, sftp),
            (0, 0, 0, 0),
        )
    )


def walk_remote_directory(directory: str, tree: Tree, sftp: paramiko.SFTPClient):
    paths = sorted(
        sftp.listdir(directory),
        key=lambda path: (path),
    )

    for filename in paths:
        path = pathlib.PurePath(directory) / filename
        stat = sftp.stat(path.as_posix())
        if get_file_type(stat) == FileType.DIR:
            style = ""  # "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: {path.name}",
                style=style,
                guide_style=style,
            )
            walk_remote_directory(path.as_posix(), branch, sftp)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            file_size = stat.st_size if stat.st_size is not None else 0
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "📄 "
            tree.add(Text(icon) + text_filename)


def get_remote_file_tree(path: str, sftp: paramiko.SFTPClient):
    if not exist_remote(path, sftp):
        raise FileNotFoundError(f"remote path({path}) do not exist")
    tree = Tree(
        f":open_file_folder: [link file://{path}]{path}",
        guide_style="bold bright_blue",
    )
    walk_remote_directory(path, tree, sftp)
    return tree


def remote_file_list_to_tree(files: list[str], pwd: str) -> Tree:
    tree = Tree(
        f":open_file_folder: [link file://{pwd}]{pwd}",
        guide_style="bold bright_blue",
    )
    t_idx = 0

    def dfs(root: Tree, par_path: str):
        nonlocal t_idx
        while t_idx < len(files) and files[t_idx].startswith(par_path):
            l_idx = files[t_idx].find("||")
            if l_idx == -1:
                branch = root.add(
                    f"[bold magenta]:open_file_folder: {files[t_idx]}",
                    style="",
                    guide_style="",
                )
                t_idx += 1
                dfs(branch, files[t_idx - 1])
            else:
                filename = files[t_idx][:l_idx]
                text_filename = Text(filename, "green")
                text_filename.highlight_regex(r"\..*$", "bold red")
                icon = "📄 "
                root.add(Text(icon) + text_filename)
                t_idx += 1

    dfs(tree, "")
    return tree
