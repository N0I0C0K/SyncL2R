import re
import sys

from typing import Literal, Mapping, Type
from os import fspath, popen

from syncl2r.types import StrPath


class FileMD5Calculator:
    @classmethod
    def gen_calc_cmd(cls, *files: StrPath) -> str:
        raise NotImplementedError

    @classmethod
    def parse(cls, cmd_output: str) -> dict[str, str]:
        raise NotImplementedError

    @classmethod
    def calc(cls, *files: StrPath) -> dict[str, str]:
        output = popen(cls.gen_calc_cmd(*files))
        return cls.parse(output.read())


class CertutilFileMD5Calculator(FileMD5Calculator):
    split_word = "-next-xjsu-split-"

    @classmethod
    def gen_calc_cmd(cls, *files: StrPath) -> str:
        return f"&echo {cls.split_word}&".join(
            map(lambda it: f"certutil -hashfile {fspath(it)} md5", files)
        )

    @classmethod
    def parse(cls, cmd_output: str) -> dict[str, str]:
        parts = cmd_output.split(cls.split_word + "\n")
        res = {}
        for part in parts:
            part_res = part.strip().split("\n")
            if len(part_res) == 3:
                res[part_res[0][6:-4]] = part_res[1]

        return res


class MD5SumFileMD5Calculator(FileMD5Calculator):
    @classmethod
    def gen_calc_cmd(cls, *files: StrPath) -> str:
        return "md5sum " + " ".join(map(lambda it: fspath(it), files))

    @classmethod
    def parse(cls, cmd_output: str) -> dict[str, str]:
        res = {}
        for line in cmd_output.split("\n"):
            line_res = line.split()
            if len(line_res) == 2:
                res[line_res[1]] = line_res[0]
        return res


class MD5FileMD5Calculator(FileMD5Calculator):
    md5_patten = re.compile(r"MD5 \((.*)\) = (.*)")

    @classmethod
    def gen_calc_cmd(cls, *files: StrPath) -> str:
        return "md5 " + " ".join(map(lambda it: fspath(it), files))

    @classmethod
    def parse(cls, cmd_output: str) -> dict[str, str]:
        res = {}
        for line in cmd_output.split("\n"):
            if (md5_res := cls.md5_patten.match(line)) is not None:
                file_path, md5_str = md5_res.groups()
                res[file_path] = md5_str
        return res


_SupportPlatform = Literal["windows", "linux", "macos"]


platform = sys.platform
if platform.startswith("linux"):
    md5_calculator = MD5SumFileMD5Calculator
elif platform.startswith("win32"):
    md5_calculator = CertutilFileMD5Calculator
elif platform.startswith("darwin"):
    md5_calculator = MD5FileMD5Calculator


def get_avilable_md5_calculator() -> Type[FileMD5Calculator]:
    platform = sys.platform
    if platform.startswith("linux"):
        return MD5SumFileMD5Calculator
    elif platform.startswith("win32"):
        return CertutilFileMD5Calculator
    elif platform.startswith("darwin"):
        return MD5FileMD5Calculator
    else:
        raise NotImplementedError


def batch_calc_local_files_md5(*files: StrPath) -> dict[str, str]:
    return md5_calculator.calc(*files)
