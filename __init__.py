# -*- coding: utf-8 -*-
"""The standard fram log library.

This library provides the following arguments.
    --all_loggers   # Apply the handlers to all non fram loggers also.

    --console       # Logs to the CLI.  If you don't specify a handler this is
                    # default.

    --debug         # Logs all messages debug and below.

    --error         # Logs all messages error and below.

    --info          # Logs all messages info and below.

    --syslog        # Specifies to send the messages to syslog.

    --syslog_host   # Specifies a syslog host url.

    --syslog_port   # Specifies a syslog port.

    --warning       # Logs all messages warning and below.

    --file_name     # Logs all messages to file.

    --syslog_facility
                    # Setup the syslog facility.

EXAMPLE:
    import fram
    from fram_logging import FramLogging

    LOGGER = FramLogging.getLogger("example")

    def main(framework):
        LOGGER.debug("example debug")
        LOGGER.info("example info")
        LOGGER.warning("example warning")
        LOGGER.error("example error")

    if __name__ == "__main__":
        fram.run(func=main)
"""
import logging
import logging.handlers
import sys
import six

__author__ = "Shawn Lee"
__email__ = "shawn@143t.com"

# The standard format that will be used in the framework.
STANDARD_FORMAT = "%(levelname)s:%(name)s %(message)s"


def get_unhandled_fram_logger():
    """Will return the first unprocessed FramLogging object."""
    try:
        for name, instance in six.iteritems(sys.modules):
            if (
                    hasattr(instance, "LOGGER") and
                    isinstance(instance.LOGGER, FramLogging)):
                # If the logger is already handled skip this one.
                if hasattr(instance.LOGGER, "processed"):
                    continue
                # Looks like this is the next unhandled logger.  Flag it as
                # handled.
                else:
                    instance.LOGGER.processed = True
                    return instance.LOGGER
    # exception handling for 2.6 compatibility
    except (AttributeError,):
        err = sys.exc_info()[1]
        print (
            "\n\n****ERROR**** Did you name your module's FramLogging "
            "instance something other than LOGGER? It needs to be exactly "
            "LOGGER since the library depends on it.\n\n")
        raise err


def get_syslog_handlers(framework):
    """Will build the syslog handler and return it."""
    if framework["argparse"].syslog_host:
        port = logging.handlers.SYSLOG_UDP_PORT
        if framework["argparse"].syslog_port:
            port = framework["argparse"].syslog_port
        return logging.handlers.SysLogHandler(address=(
            framework["argparse"].syslog_host, port))
    else:
        return logging.handlers.SysLogHandler(address=("/dev/log"))


def get_level(framework):
    """Get the logging level."""
    if framework["argparse"].debug:
        return logging.DEBUG
    elif framework["argparse"].warning:
        return logging.WARNING
    elif framework["argparse"].error:
        return logging.ERROR
    elif framework["argparse"].info:
        return logging.INFO
    # Default is WARNING.
    return logging.WARNING


def get_handlers(framework):
    """Return a list of handlers based on the current framework."""
    handlers = []
    if framework["argparse"].syslog:
        handlers.append(get_syslog_handlers(framework))
    if framework["argparse"].file_name:
        handlers.append(logging.FileHandler(
            framework["argparse"].file_name))
    if not handlers or framework["argparse"].console:
        handlers.append(logging.StreamHandler())
    return handlers


def main_decorator(func):
    """Decorate the main function to setup the logger properlly."""
    def wrapped(framework):
        """Wrapped."""
        # LOGGER is expected to be set in the calling code using framLogging.
        handlers = get_handlers(framework)
        if framework["argparse"].all_loggers:
            apply_handlers(framework, logging.getLogger(), handlers)
        while True:
            module_logger = get_unhandled_fram_logger()
            if not module_logger:
                break
            # Make sure console is a default handler if non given.
            apply_handlers(framework, module_logger, handlers)
        return func(framework)
    return wrapped


def apply_handlers(framework, logger, handlers):
    """Apply all the handlers to the logger."""
    level = get_level(framework)
    # Make sure console is a default handler if non given.
    for handler in handlers:
        formatter = logging.Formatter(STANDARD_FORMAT)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


class FramLogging(logging.getLoggerClass()):
    """Wrap the logging module to add the fram plugin features."""

    def __init__(self, name, logger):
        """Build a logger."""
        # no super() for 2.6 compatbility
        logging.getLoggerClass().__init__(self, name)
        self.logger = logger

    def __getattr__(self, name, *args, **kwargs):
        """Expose all other functions provided by the standard logging."""
        return getattr(self.logger, name)(*args, **kwargs)

    @classmethod
    def getLogger(cls, name):
        """Override parent method and call our init."""
        return FramLogging(name, logging.getLogger(name))


FRAM_PLUGIN = {
    "argparse": {
        "--debug": {
            "help": "Turn on verbose debugging.", "action": "store_true"},
        "--warning": {
            "help": "Turn on warning messages.", "action": "store_true"},
        "--info": {"help": "Turn on info messages.", "action": "store_true"},
        "--console": {
            "help": "Log messages to console.", "action": "store_true"},
        "--syslog": {
            "help": "Turn on syslog messages.", "action": "store_true"},
        "--syslog_host": {"help": "Syslog host to send meessages to."},
        "--syslog_port": {
            "help": "Specify the port for syslog to connect to."},
        "--syslog_facility": {
            "help": "The facility to use for the messages.",
            "choices": ["LOG_KERN", "LOG_USER", "LOG_MAIL", "LOG_DAEMON",
                        "LOG_AUTH", "LOG_LPR", "LOG_NEWS", "LOG_UUCP",
                        "LOG_CRON", "LOG_SYSLOG ", "LOG_LOCAL0",
                        "LOG_LOCAL1", "LOG_LOCAL2", "LOG_LOCAL3", "LOG_LOCAL4",
                        "LOG_LOCAL5", "LOG_LOCAL6", "LOG_LOCAL7"]},
        "--file_name": {
            "help": "Specify a file to write logs to."},
        "--error": {
            "help": "Turn on error messages.", "action": "store_true"},
        "--all_loggers": {
            "help": "Apply the handlers to all non fram loggers also.",
            "action": "store_true"}},
    "main_decorator": main_decorator}
