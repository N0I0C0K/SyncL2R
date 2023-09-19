# SyncL2R

```txt
   _____                      __    ___    ____ 
  / ___/ __  __ ____   _____ / /   |__ \  / __ \
  \__ \ / / / // __ \ / ___// /    __/ / / /_/ /
 ___/ // /_/ // / / // /__ / /___ / __/ / _, _/ 
/____/ \__, //_/ /_/ \___//_____//____//_/ |_|  
      /____/                                    
```

一个本地和远程文件同步，部署工具，集多种功能于一身的工具

- 可配置忽略文件
- 支持正则表达式匹配
- 手动同步文件，从远程提取文件
- 一键部署任务触发
- 支持自定义动作
- 漂亮的终端输出

## 适用场景

> 试想你有一个后端/前端项目，在本地开发完成之后，你需要将项目部署到服务器上，一般来讲有以下步骤
> 1. 上传代码到服务器上
> 2. 登录服务器
> 3. 手动进行部署

SyncL2R就是将上面的步骤**缩短到一行命令**。

适用范围：

- 在本地开发，在服务器上部署
- 项目规模不大，没有自己的流水线

## Command

详细的命令列表和帮助文档可以，使用help命令查看

```shell
syncl2r --help
```

命令列表
| command | doc                                                    |
| ------- | ------------------------------------------------------ |
| push    | 推送本地文件到远程（多种模式选择，可自动触发部署任务） |
| pull    | 拉取远程文件到本地                                     |
| init    | 在当前目录下，初始化配置文件                           |
| exec    | 执行自定义动作                                         |

### Push

```shell
syncl2r push
```

支持三种模式：

- soft 只更新上传新增的文件
- normal 只更新发生改变的文件
- hard 删除远程目录下的所有文件，再上传全量文件

![Alt text](./imgs/push.gif)

### Pull

```shell
syncl2r pull
```

![Alt text](./imgs/pull.gif)

### Shell

```shell
syncl2r shell
```

使用提供的config（不填为默认的config文件）, 打开一个远程终端

## Event

Syncl2r支持事件触发，用来执行shell命令，目前支持以下事件：

- `push_complete_exec`，在`Push`任务执行完成之后执行
- `push_start_exec`，在`Push`任务执行之前执行

## Config

config文件名称默认为`config.l2r.yaml`，**如果命令中不指定config会默认寻找当前目录下第一个满足`*.l2r.yaml`的文件**

```yaml
connect_config:
  ip: 127.0.0.1                   # 远程主机ip
  username: root                  # 登录用户
  password: 'test123'             # 密码
  port: 11022                     # ssh端口，不填默认22
file_sync_config:
  exclude: ['*.config']           # 同步排除文件，支持正则匹配
  remote_root_path: '/home/test'  # 远程根路径
  root_path: .                    # 本地同步根路径
events:                           # 事件只要填写默认每次都会执行（可以设置不执行）
  push_complete_exec:             # 上传完毕后执行命令
    - pwd
  push_start_exec:                # 上传开始执行命令
    - echo hello world
    - sleep 1
    - pwd
```

## install

```shell
python -m pip install .
```

**require**

```shell
python >= 3.10
```
