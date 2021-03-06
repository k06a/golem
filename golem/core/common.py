from calendar import timegm
from datetime import datetime
import errno
import os
from os import path
from pathlib import Path
import pytz
import sys
import logging.config


def is_windows():
    """
    Check if this system is Windows
    :return bool: True if current system is Windows, False otherwise
    """
    return sys.platform == "win32"


def is_osx():
    """
    Check if this system is OS X
    :return bool: True if current system is OS X, False otherwise
    """
    return sys.platform == "darwin"


def is_linux():
    """
    Check if this system is Linux
    :return bool: True if current system is Linux, False otherwise
    """
    return sys.platform.startswith('linux')


def get_golem_path():
    """
    Return path to main golem directory
    :return str: path to main golem directory
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def nt_path_to_posix_path(path):
    """Replaces all "\"'s in a specified path by "/"'s and replaces
    the leading "X:" (driver letter), if present, with "/x".
    :param str path:
    :return str:
    """
    path = path.replace("\\", "/")
    parts = path.split(":")
    if len(parts) > 1:
        return "/" + parts[0].lower() + parts[1]
    return path


def get_timestamp_utc():
    now = datetime.now(pytz.utc)
    return timegm(now.utctimetuple()) + now.microsecond / 1000000.0


def timeout_to_deadline(timeout):
    return get_timestamp_utc() + timeout


def deadline_to_timeout(timestamp):
    return timestamp - get_timestamp_utc()


def timestamp_to_datetime(ts):
    return datetime.fromtimestamp(ts, pytz.utc)


class HandleError(object):
    def __init__(self, error, handle_error):
        self.handle_error = handle_error
        self.error = error

    def __call__(self, func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self.error:
                return self.handle_error(*args, **kwargs)
        return func_wrapper


class HandleKeyError(HandleError):
    def __init__(self, handle_error):
        super(HandleKeyError, self).__init__(KeyError, handle_error)


class HandleAttributeError(HandleError):
    def __init__(self, handle_error):
        super(HandleAttributeError, self).__init__(AttributeError, handle_error)


def config_logging(suffix='', datadir=None):
    """Config logger"""
    try:
        from loggingconfig_local import LOGGING
    except ImportError:
        from loggingconfig import LOGGING

    logdir_path = Path('logs')
    if datadir is not None:
        logdir_path = Path(datadir) / logdir_path
        datadir += '/'
    else:
        datadir = ''
    if not logdir_path.exists():
        logdir_path.mkdir(parents=True)

    for handler in LOGGING.get('handlers', {}).values():
        if 'filename' in handler:
            handler['filename'] %= {
                'datadir': datadir,
                'suffix': suffix,
            }

    logging.config.dictConfig(LOGGING)
    logging.captureWarnings(True)
