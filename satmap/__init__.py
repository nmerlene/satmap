"""
Simple package-wide utilities
"""

from __future__ import print_function, division, absolute_import

import time
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter, ArgumentDefaultsHelpFormatter


# Initialize logger
logging.getLogger(__name__).addHandler(logging.NullHandler)
LOGGER = logging.getLogger()


class ArgumentFormatter(RawDescriptionHelpFormatter, ArgumentDefaultsHelpFormatter):
    """
    Simple class to add raw description formatting and argument default help formatting to
      the argument parser
    """


def get_parent_argparse():
    """
    Return parent argument parser

    Returns:
        ArgumentParser: Parent argument parser
    """
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentFormatter, add_help=False
    )
    parser.add_argument("-v", "--verbose", help="Verbosity", action="count", default=0)
    parser.add_argument("-q", "--quiet", help="Quiet", action="count", default=0)
    return parser


def set_log_level(verbose_level, quiet_level):
    """
    Set logger level based on verbosity and quiet counts

    Args:
        verbose_level (int): Verbose level
        quiet_level (int):   Quiet level

    """
    # Set combined log level based on verbose and quiet levels
    combined_level = verbose_level - quiet_level
    if combined_level <= -3:
        log_level = logging.CRITICAL + 10
    elif -3 < combined_level <= -2:
        log_level = logging.CRITICAL
    elif -2 < combined_level <= -1:
        log_level = logging.ERROR
    elif -1 < combined_level < 1:
        log_level = logging.WARNING
    elif 1 <= combined_level < 2:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    # Set logger configuration
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s:%(levelname)s:%(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def script_setup(verbose_level, quiet_level):
    """
    Script setup

    Args:
        verbose_level (int): Verbose level
        quiet_level (int):   Quiet level

    Returns:
        float: Start time
    """
    set_log_level(verbose_level, quiet_level)
    start_time = time.time()
    LOGGER.info("Starting at %s", time.asctime(time.localtime(start_time)))
    return start_time


def script_teardown(start_time):
    """
    Script teardown

    Args:
        start_time:
    """
    stop_time = time.time()
    LOGGER.info("Finished at %s", time.asctime(time.localtime(stop_time)))
    elapsed_time = stop_time - start_time
    LOGGER.info("Elapsed time: %.2f seconds", elapsed_time)
