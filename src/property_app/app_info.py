import time
from dataclasses import dataclass
from datetime import date, datetime

from property_app.config import env_str


@dataclass
class AppInfo:

    project: str = env_str("FLASK_APP", "app")
    commit_hash: str = env_str("APP_BUILD_HASH", "dev")
    build_date: date = datetime.today()
    build_epoch_sec: int = int(time.time())
