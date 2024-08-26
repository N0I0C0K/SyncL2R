import typing
from .executor import execute_bash, execute_cmd

remote_tree = """
#!/bin/bash

# 获取当前目录的绝对路径
root=$(pwd)

# 设置匹配模式
patterns=(%s)

# 检查路径是否匹配任意模式
path_matches_patterns() {
    local path="$1"  # 文件或目录路径

    for pattern in "${patterns[@]}"
    do
        # 使用模式匹配进行比较
        if [[ $path == $pattern ]]; then
            return 0
        fi
    done

    return 1
}

# 递归函数，遍历目录下的文件和子目录
traverse_directory() {
    local directory="$1"  # 当前目录路径

    # 检查目录路径是否匹配模式，如果匹配，则跳过该目录
    if path_matches_patterns "$(basename "$directory")"; then
        return
    fi
    
    # 遍历目录下的所有文件和子目录
    for file in "$directory"/* "$directory"/.[!.]*;
    do
        if [ -d "$file" ]; then
	        echo "$file"

            # 如果是子目录，递归调用自身
            traverse_directory "$file"
	
        elif [ -f "$file" ]; then
            # 如果是文件，检查路径是否匹配模式，跳过匹配的文件
            if path_matches_patterns "$file"; then
                continue
            fi

            # 计算文件的MD5值
            md5=$(md5sum "$file" | awk '{print $1}')
            # 输出相对路径和MD5值
            echo "$file||$md5"
        fi
    done
}

# 调用递归函数，并传递当前目录路径
traverse_directory "$(pwd)"
"""


class FileWithMD5(typing.NamedTuple):
    path: str
    md5: str | None

    @classmethod
    def build_from_str(cls, s: str):
        pair = s.split("||")
        path = pair[0]
        md5 = pair[1] if len(pair) > 1 else None
        return cls(path, md5)

    def __fspath__(self) -> str:
        return self.path

    def is_dir(self) -> bool:
        return self.md5 is None


def get_remote_files_with_md5(exclude_pattens: list[str]) -> list[FileWithMD5]:
    comm_path = execute_cmd("pwd")

    out = execute_bash(
        remote_tree,
        " ".join(map(lambda x: f'"{x}"', exclude_pattens)),
    )

    files = list(
        map(
            lambda x: FileWithMD5.build_from_str(
                x.removeprefix(comm_path).removeprefix("/")
            ),
            out.split("\n"),
        )
    )
    return files
