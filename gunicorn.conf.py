import multiprocessing
import os

logger_class = "property_app.logging.GunicornLogger"
flask_env = os.environ.get("APP_ENV")
workers = 2
worker_class = "gthread"
threads = multiprocessing.cpu_count() * 2
bind = ":5000"
proc_name = "property-app"
timeout = 60
graceful_timeout = 30
keepalive = 5
worker_tmp_dir = "/dev/shm"

accesslog = "-"
errorlog = "-"
