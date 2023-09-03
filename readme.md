# SyncL2R

同步本地文件夹和远程主机的文件夹内容，支持增量上传模式（只上传更改的文件）。

- 可配置忽略文件
- 支持正则表达式匹配
- 手动同步文件，从远程提取文件
- 可以设置自动同步（需要后台任务）
- 可以设置受监视文件夹更改的自动同步（需要后台任务）
- 漂亮的终端输出

## Command

查看更多帮助
`syncl2r --help`
命令列表
| command | doc | usage |
| ------- | ------------------------------ | ----- |
| push | sync local file to remote host |
| pull | pull remote file |
| init | init l2r_config.json |

### Push

```
> syncl2r push
```

支持三种模式：
- soft 只更新上传新增的文件
- normal 只更新发生改变的文件
- hard 删除远程目录下的所有文件，再上传全量文件 

![Alt text](./imgs/push.gif)

### Pull

**Usage**
`syncl2r pull`
![Alt text](./imgs/pull.gif)

## install

**安装**
`python setup.py install`

**require**

```
python >= 3.10
```
