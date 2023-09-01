# SyncL2R

[中文](./readme_cn.md)

Synchronize folder contents of local folders and remote hosts

- You can choose to synchronize files
- Support regular expression matching
- Manually synchronize files, pull file from remote
- Automatic synchronization can be set(background task require)
- Automatic synchronization of monitored folder changes can be set(background task require)
- Beautiful terminal output

## Command

for more help, type
`syncl2r --help`

| command | doc                            | usage |
| ------- | ------------------------------ | ----- |
| push    | sync local file to remote host |
| pull    | pull remote file               |
| init    | init l2r_config.json           |

### Push

push local file to the remote host.

#### Push Mode

| mode     | doc                                            |
| -------- | ---------------------------------------------- |
| 1:force  | will del remote upload path, then upload files |
| 2:normal | will only upload changed file                  |
| 3:soft   | will only uplaod new file                      |

**Usage**
`syncl2r push`
![Alt text](./imgs/push.gif)

### Pull

pull files from remote host. default to all files.
**Usage**
`syncl2r pull [files]`
![Alt text](./imgs/pull.gif)

## Config File

```json
{
  "connect_config": {
    "ip": "", // remote ip address
    "port": 22, // ssh port
    "username": "username", // remote ssh username
    "password": "password" // password
  },
  "file_sync_config": {
    "root_path": "./test", //folder to sync
    "remote_root_path": "/home/test11", // Synchronize to remote folder.(This folder will be created if it does not exist)
    "exclude": ["*.txt", ".gitignore"] //files to ignore
  }
}
```

## install

```
python setup.py install
```

**require**

```
python >= 3.10
```
