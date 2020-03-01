import time
from dataclasses import dataclass
from datetime import date, datetime

from property_app.config import get_config

config = get_config()


@dataclass
class AppInfo:

    project: str = config.ASGI_APP
    commit_hash: str = config.APP_BUILD_HASH
    build_date: date = datetime.today()
    build_epoch_sec: int = int(time.time())
