from .app import app
from .app import app
from ..console import pprint
from ..config import load_config
from ..connect_core import Connection
from ..sync_core import SyncTask, SyncMode

from ..utils.sftp_utils import walk_remote_directory


@app.command()
def test():
    config = load_config()
    conn = Connection()
