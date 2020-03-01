"""
Logger and LoggerMixin should be the only access to the logging system the app.

"""
import datetime
import logging
import threading
from typing import Optional

import structlog

from .app_info import AppInfo


def loggers():
    """ get list of all loggers """
    root = logging.root
    existing = root.manager.loggerDict.keys()  # noqa
    return [logging.getLogger(name) for name in existing]


class LogEntryProcessor:

    _APP_INFO = AppInfo()
    _THREAD = threading.local()

    @staticmethod
    def get_request_id() -> Optional[str]:
        if hasattr(LogEntryProcessor._THREAD, "request_id"):
            return LogEntryProcessor._THREAD.request_id

        return None

    @staticmethod
    def set_request_id(request_id: str) -> None:
        LogEntryProcessor._THREAD.request_id = request_id

    @staticmethod
    def add_app_info(_, __, event_dict: dict) -> dict:

        event_dict["app"] = LogEntryProcessor._APP_INFO.project
        event_dict["commit_hash"] = LogEntryProcessor._APP_INFO.commit_hash

        if LogEntryProcessor.get_request_id():
            event_dict["request_id"] = LogEntryProcessor.get_request_id()

        return event_dict

    @staticmethod
    def add_logger_name(logger, _, event_dict: dict) -> dict:

        event_dict["logger_name"] = logger.name

        return event_dict

    @staticmethod
    def add_timestamp(_, __, event_dict: dict) -> dict:
        """
        Add timestamp to the event dict - using an Analytics appropriate time stamp
        """
        now = datetime.datetime.utcnow()
        event_dict["timestamp"] = now.strftime("%Y-%m-%dT%H:%M:%S")

        return event_dict

    @staticmethod
    def redact_pii(_, __, event_dict: dict) -> dict:
        """
        Hide any pii that appear in log entries
        """
        sensitive_keys = ["password", "phone"]
        for key in sensitive_keys:
            if event_dict.get(key):
                event_dict[key] = "*******"

        return event_dict


def initialize_logging(colors: bool = True, log_mode: str = None) -> None:
    import logging.config
    from property_app.config import env_str

    if log_mode is None:
        log_mode = env_str("LOG_MODE", "local")

    level = env_str("LOG_LEVEL", "INFO")
    app_log_level = env_str("APP_LOG_LEVEL", level)

    gunicorn_level = env_str("GUNICORN_LOG_LEVEL", "INFO")

    log_processor_chain = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        LogEntryProcessor.add_app_info,
    ]

    if log_mode != "local":
        log_processor_chain += [LogEntryProcessor.redact_pii]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "root": {"level": level, "handlers": ["console"]},
            "loggers": {
                "gunicorn.error": {
                    "level": gunicorn_level,
                    "qualname": "gunicorn.error",
                    "handlers": ["console_error"],
                },
                "property_app": {"level": app_log_level, "qualname": "property_app"},
                "rq.worker": {"level": app_log_level, "qualname": "rq.worker"},
                "parso": {"level": logging.ERROR},
            },
            "formatters": {
                "local": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=colors),
                    "foreign_pre_chain": log_processor_chain,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                    "foreign_pre_chain": log_processor_chain,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": log_mode,
                    "stream": "ext://sys.stdout",
                },
                "console_error": {
                    "class": "logging.StreamHandler",
                    "formatter": log_mode,
                    "stream": "ext://sys.stderr",
                },
            },
        }
    )

    chain = log_processor_chain + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ]

    structlog.configure_once(
        processors=chain,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class LoggerMixin:
    """
    Adds a scoped structlog logger to a class.
    """

    @property
    def _logger(self):
        if not getattr(self, "__app_logger__", None):
            self.__app_logger__ = structlog.get_logger(type(self).__name__)
        return self.__app_logger__

    def _debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, level=logging.DEBUG, **kwargs)

    def _error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, level=logging.ERROR, **kwargs)

    def _info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, level=logging.INFO, **kwargs)

    def _warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, level=logging.WARN, **kwargs)


class Logger(LoggerMixin):
    """
    Logger for non-class based things. (so a lot of things...)
    """

    def __init__(self, name):
        """
        :param name: required logger name - use dotted package path
        """
        if name is not None and not getattr(self, "__app_logger__", None):
            self.__app_logger__ = structlog.get_logger(name)

    def debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)


def get_logger(name: str) -> Logger:
    return Logger(name)


class GunicornLogger(object):
    """
    Custom logger for gunicorn

    See: https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py
    """

    def __init__(self, cfg):
        initialize_logging()
        self._logger = structlog.get_logger("gunicorn.error")
        self.cfg = cfg

    def critical(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs) -> None:
        self._logger.exception(msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs) -> None:
        self._logger.log(lvl, msg, *args, **kwargs)

    def access(self, resp, req, environ, request_time) -> None:
        pass

    def reopen_files(self) -> None:
        pass

    def close_on_exec(self) -> None:
        pass
