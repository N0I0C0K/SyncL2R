# SyncL2R

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

## install

**Run**
`python setup.py install`

**require**

```
python >= 3.10
```
