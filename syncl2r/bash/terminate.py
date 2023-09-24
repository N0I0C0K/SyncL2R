from .executor import execute_bash

sh = """
#!/bin/bash

terminate_process() {
    local parent_pid=$1
    
    # 获取parent_pid的所有子进程PID
    local child_pids=$(pgrep -P "$parent_pid")
    
    # 递归终止子进程
    for child_pid in $child_pids; do
        terminate_process "$child_pid"
    done
    
    # 终止当前进程
    kill "$parent_pid" 2>/dev/null
}

# 要终止的进程PID
target_pid=(%s)

for pid in "${target_pid[@]}"; do
    # 终止进程及其子进程
    terminate_process "$pid"
done
"""


def kill_pid_and_child(pids: list[str]):
    execute_bash(sh, " ".join(map(lambda x: f'"{x}"', pids)))
