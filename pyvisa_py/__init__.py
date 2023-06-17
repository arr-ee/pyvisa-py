# -*- coding: utf-8 -*-
"""Pure Python backend for PyVISA.


:copyright: 2014-2020 by PyVISA-py Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
import sys
from structlog import configure, stdlib, processors
from structlog.contextvars import merge_contextvars

configure(
    wrapper_class=stdlib.BoundLogger,
    logger_factory=stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
    processors=[
        merge_contextvars,
        stdlib.filter_by_level,
        # Add the name of the logger to event dict.
        stdlib.add_logger_name,
        # Add log level to event dict.
        stdlib.add_log_level,
        # Perform %-style formatting.
        stdlib.PositionalArgumentsFormatter(),
        # Add a timestamp in ISO 8601 format.
        processors.TimeStamper(fmt="iso"),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        processors.StackInfoRenderer(),
        # If the "exc_info" key in the event dict is either true or a
        # sys.exc_info() tuple, remove "exc_info" and render the exception
        # with traceback into the "exception" key.
        processors.format_exc_info,
        # If some value is in bytes, decode it to a unicode str.
        processors.UnicodeDecoder(),
        # Render the final event dict as JSON.
        processors.KeyValueRenderer(
            sort_keys=True,
            key_order=[
                "level",
                "timestamp",
                "logger",
                "event",
            ],
        ),
    ],
)

if sys.version_info >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version
else:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

__version__ = "unknown"
try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass

# noqa: we need to import so that __init_subclass__() is executed once
from . import attributes  # noqa: F401
from .highlevel import PyVisaLibrary

WRAPPER_CLASS = PyVisaLibrary
