from .app import app
from .app import app
from ..connect_core import Connection
from ..bash import get_remote_tree
from ..sync_core.deploy_core import check_still_running
from ..config import get_global_config
from ..console import pprint


@app.command()
def test():
    # config = load_config()
    conn = Connection()
    config = get_global_config()
    pprint(check_still_running(conn))
