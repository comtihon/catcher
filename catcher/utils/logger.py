import logging
from logging import Logger

import catcher


def configure(log_level: str):
    level = None
    if log_level == 'critical':
        level = logging.CRITICAL
    if log_level == 'error':
        level = logging.ERROR
    if log_level == 'warning':
        level = logging.WARNING
    if log_level == 'info':
        level = logging.INFO
    if log_level == 'debug':
        level = logging.DEBUG
    if not log_level:
        raise RuntimeError('Unknown logging level ' + log_level)
    logging.basicConfig(level=level)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger() -> Logger:
    return logging.getLogger(catcher.APPNAME)


def debug(msg: str):
    get_logger().debug(msg)


def info(msg: str):
    get_logger().info(msg)


def warning(msg: str):
    get_logger().warning(msg)


def error(msg: str):
    get_logger().error(msg)


def critical(msg: str):
    get_logger().critical(msg)
