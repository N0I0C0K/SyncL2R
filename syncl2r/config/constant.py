from pathlib import PurePath

SyncL2R_l2r_Path = PurePath("./.l2r")
Remote_Config_Data_Path = SyncL2R_l2r_Path / "data.yaml"
History_Log_Path = SyncL2R_l2r_Path / "logs"
Config_Path = SyncL2R_l2r_Path / "config.l2r.yaml"
Temp_Output_Path = SyncL2R_l2r_Path / "out.log"
Temp_Pids_Path = SyncL2R_l2r_Path / "pids.txt"
Local_Root_Abs_Path = PurePath(".")
Remote_Root_Abs_Path = PurePath(".")


def update_local_root_path(s: str | PurePath):
    global Local_Root_Abs_Path
    if isinstance(s, str):
        Local_Root_Abs_Path = PurePath(s)
    elif isinstance(s, PurePath):
        Local_Root_Abs_Path = s


def update_remote_root_path(s: str | PurePath):
    global Remote_Root_Abs_Path
    if isinstance(s, str):
        Remote_Root_Abs_Path = PurePath(s)
    elif isinstance(s, PurePath):
        Remote_Root_Abs_Path = s
