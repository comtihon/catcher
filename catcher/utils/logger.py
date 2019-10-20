import logging
from logging import Logger

import catcher
from catcher.modules.log_storage import EmptyLogStorage

log_storage = EmptyLogStorage('empty')


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
    log_storage.output('debug', msg)
    get_logger().debug(msg)


def info(msg: str):
    log_storage.output('info', msg)
    get_logger().info(msg)


def warning(msg: str):
    log_storage.output('warning', msg)
    get_logger().warning(msg)


def error(msg: str):
    log_storage.output('error', msg)
    get_logger().error(msg)


def critical(msg: str):
    log_storage.output('critical', msg)
    get_logger().critical(msg)
