import logging
from contextlib import ContextDecorator
from logging import Logger

import catcher
from catcher.modules.log_storage import EmptyLogStorage
from colorama import Fore, Style

log_storage = EmptyLogStorage('empty')
colored_output = True  # use colorama for colored output. Is controlled by --no-color cmd arg
output_enabled = True  # output/no output switcher. Is controlled by -q/-qq cmd arg


class OptionalOutput(ContextDecorator):
    def __init__(self, active: bool):
        self.active = active

    def __enter__(self):
        global output_enabled
        if self.active:
            output_enabled = False

    def __exit__(self, exc_type, exc, exc_tb):
        if self.active:
            global output_enabled
            output_enabled = True


def blue(output: str) -> str:
    return Fore.BLUE + output + Style.RESET_ALL if colored_output else output


def green(output: str) -> str:
    return Fore.GREEN + output + Style.RESET_ALL if colored_output else output


def light_green(output: str) -> str:
    return Fore.LIGHTGREEN_EX + output + Style.RESET_ALL if colored_output else output


def red(output: str) -> str:
    return Fore.RED + output + Style.RESET_ALL if colored_output else output


def yellow(output: str) -> str:
    return Fore.YELLOW + output + Style.RESET_ALL if colored_output else output


def configure(log_level: str, use_color: bool = True):
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
    global colored_output
    colored_output = use_color


def get_logger() -> Logger:
    return logging.getLogger(catcher.APPNAME)


def debug(msg: str):
    log_storage.output('debug', msg)
    if output_enabled:
        get_logger().debug(_nested_output(msg))


def info(msg: str):
    log_storage.output('info', msg)
    if output_enabled:
        get_logger().info(_nested_output(msg))


def warning(msg: str):
    log_storage.output('warning', msg)
    if output_enabled:
        get_logger().warning(_nested_output(msg))


def error(msg: str):
    log_storage.output('error', msg)
    if output_enabled:
        get_logger().error(_nested_output(msg))


def critical(msg: str):
    log_storage.output('critical', msg)
    if output_enabled:
        get_logger().critical(_nested_output(msg))


def _nested_output(msg):
    if log_storage.nesting_counter > 0:
        spaces = ''.join(['\t' for i in range(0, log_storage.nesting_counter - 1)])
        msg = spaces + '|--> ' + str(msg)
    return msg
