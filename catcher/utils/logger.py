import logging
from logging import Logger

import catcher
from catcher.modules.log_storage import EmptyLogStorage
from colorama import Fore, Style

log_storage = EmptyLogStorage('empty')


def green(output: str) -> str:
    return Fore.GREEN + output + Style.RESET_ALL


def red(output: str) -> str:
    return Fore.RED + output + Style.RESET_ALL


def yellow(output: str) -> str:
    return Fore.YELLOW + output + Style.RESET_ALL


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
    get_logger().debug(_nested_output(msg))


def info(msg: str):
    log_storage.output('info', msg)
    get_logger().info(_nested_output(msg))


def warning(msg: str):
    log_storage.output('warning', msg)
    get_logger().warning(_nested_output(msg))


def error(msg: str):
    log_storage.output('error', msg)
    get_logger().error(_nested_output(msg))


def critical(msg: str):
    log_storage.output('critical', msg)
    get_logger().critical(_nested_output(msg))


def _nested_output(msg):
    if log_storage.nesting_counter > 0:
        spaces = ''.join(['\t' for i in range(0, log_storage.nesting_counter - 1)])
        msg = spaces + '|--> ' + str(msg)
    return msg
