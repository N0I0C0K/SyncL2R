import paramiko
import shlex

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
    for file in "$directory"/*
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


def get_remote_tree(ssh: paramiko.SSHClient, pattens: list[str], pwd: str) -> list[str]:
    # sftp.put()
    sh_file = "js93h378df_get_remote_tree.sh"
    comm_path = ssh.exec_command(f"cd {pwd}; pwd")[1].read().decode().removesuffix("\n")
    sh = shlex.quote(remote_tree % (" ".join(map(lambda x: f'"{x}"', pattens))))
    ssh.exec_command(f"cd {pwd}; echo {sh} > {sh_file}")
    _, out, _ = ssh.exec_command(f"cd {pwd}; bash {sh_file}")
    files = list(
        map(
            lambda x: x.removeprefix(comm_path).removeprefix("/"),
            out.read().decode().split("\n"),
        )
    )
    return files
