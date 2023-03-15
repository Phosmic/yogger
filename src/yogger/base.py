"""Yogger Base Module

This module contains the base classes and functions for Yogger.
"""
import contextlib
import inspect
import io
import logging
import os
import tempfile
from collections.abc import Generator
from types import ModuleType as Module

from .constants import (
    DATE_FMT,
    DUMP_MSG,
    LOG_FMT,
)
from .pformat import pformat

_logger: Module | logging.Logger = logging

_global_package_name: str | None = None
_global_dump_path: str | None = None
_global_dump_locals: bool = False


class Yogger(logging.Logger):
    """Yogger Logger Class

    This class is used to override the default `logging.Logger` class.
    """

    def _log_with_stack(self, level: int, msg: object, *args, **kwargs) -> None:
        super().log(level, msg, *args, **kwargs)

        # Dump current stack if 'dump_locals' was set to True
        if _global_dump_locals:
            stack = inspect.stack()
            if len(stack) > 2:
                path = _dump(stack=stack[2:][::-1], err=None, dump_path=None)
                super().log(level, DUMP_MSG, path=path)

    def warning(self, *args, **kwargs) -> None:
        self._log_with_stack(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        self._log_with_stack(logging.ERROR, *args, **kwargs)

    def critical(self, *args, **kwargs) -> None:
        self._log_with_stack(logging.CRITICAL, *args, **kwargs)

    def log(self, level: int, msg: object, *args, **kwargs) -> None:
        if level >= logging.WARNING:
            self._log_with_stack(level, msg, *args, **kwargs)
        else:
            super().log(level, msg, *args, **kwargs)


def install() -> None:
    """Install the Yogger Logger Class and Instantiate the Global Logger"""
    logging.setLoggerClass(Yogger)

    global _logger
    _logger = logging.getLogger(__name__)


def configure(
    package_name: str,
    *,
    verbosity: int = 0,
    dump_locals: bool = False,
    dump_path: str | bytes | os.PathLike | None = None,
    remove_handlers: bool = True,
) -> None:
    """Prepare for Logging

    Args:
        package_name (str): Name of the package to dump from the stack.
        verbosity (int, optional): Level of verbosity (0-2) for log messages. Defaults to 0.
        dump_locals (bool, optional): Dump the caller's stack when logging with a level of warning or higher. Defaults to False.
        dump_path (str | bytes | os.PathLike, optional): Custom path to use when dumping with 'dump_on_exception' or when 'dump_locals=True', otherwise use a temporary path if None. Defaults to None.
        remove_handlers (bool, optional): Remove existing logging handlers before adding the new stream handler. Defaults to True.
    """
    global _global_package_name
    _global_package_name = package_name

    global _global_dump_locals
    _global_dump_locals = dump_locals

    if dump_path is not None:
        global _global_dump_path
        _global_dump_path = _resolve_path(dump_path)

    # Get the root logger
    root_logger = logging.getLogger()

    # Set logging levels using verbosity
    if verbosity > 0:
        level = logging.INFO if verbosity == 1 else logging.DEBUG
        _set_levels(root_logger, level)

    # Remove existing handlers
    if remove_handlers:
        _remove_handlers(root_logger)

    # Add a new stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt=LOG_FMT, datefmt=DATE_FMT, style="{"))
    root_logger.addHandler(handler)

    # Set logging level for third-party libraries
    level = logging.INFO if verbosity <= 1 else logging.DEBUG
    logging.getLogger("requests").setLevel(level)
    logging.getLogger("urllib3").setLevel(level)


def _exception_dumps(*, err: Exception) -> str:
    """Create a String Representation of an Exception

    Args:
        err (Exception): Exception that was raised.

    Returns:
        str: Representation of the stack.
    """
    msg = ""
    msg += "Exception:\n"
    msg += f"  {type(err).__module__}.{type(err).__name__}: {err!s}\n"
    msg += f"  args: {err.args!r}"
    return msg


def _stack_dumps(
    stack: list[inspect.FrameInfo],
    package_name: str | None = None,
) -> str:
    """Create a String Representation of Frames in a Stack

    Args:
        stack (list[inspect.FrameInfo]): Stack to represent.
        package_name (str | None, optional): Name of the package to dump from the stack, otherwise non-exclusive if set to None. Defaults to None.

    Returns:
        str: Representation of the stack.
    """
    msg = ""
    modules = [inspect.getmodule(frame_record[0]) for frame_record in stack]
    for i, (module, frame_record) in enumerate(zip(modules, stack)):
        if module is None:
            # Moduleless frame, e.g. dataclass.__init__
            for j in reversed(range(i)):
                if modules[j] is not None:
                    break
            else:
                # No previous module scope
                continue

            module = modules[j]

        # Only frames relating to the user's package if package_name is provided
        if (
            (package_name is None)
            or module.__name__.startswith(f"{package_name}.")
            or (module.__name__ == package_name)
        ):
            locals_ = frame_record[0].f_locals
            msg += f'Locals from file "{frame_record.filename}", line {frame_record.lineno}, in {frame_record.function}:\n'
            for var_name in locals_:
                var_value = locals_[var_name]
                msg += f"  {var_name} {type(var_value)} = "
                msg += pformat(var_name, var_value).replace("\n", "\n  ")
                msg += "\n"

            msg += "\n"
            if ("self" in locals_) and hasattr(locals_["self"], "__dict__"):
                msg += "Object dict:\n"
                msg += repr(locals_["self"].__dict__)

    return msg.rstrip("\n")


def dumps(
    stack: list[inspect.FrameInfo],
    *,
    err: Exception | None = None,
    package_name: str | None = None,
) -> str:
    """Create a String Representation of an Interpreter Stack

    Externalizes '_stack_dumps' to be accessed by the user.

    Args:
        stack (list[inspect.FrameInfo]): Stack of frames to represent.
        err (Exception | None, optional): Exception that was raised. Defaults to None.
        package_name (str | None, optional): Name of the package to dump from the stack, otherwise non-exclusive if set to None. Defaults to None.

    Returns:
        str: Representation of the stack.
    """
    msg = ""
    msg += _stack_dumps(stack=stack, package_name=package_name)
    if err is not None:
        msg += "\n\n"
        msg += _exception_dumps(err=err)
    return msg


def dump(
    fp: io.TextIOBase | io.BytesIO,  # wvutils.dtypes.FileObject
    stack: list[inspect.FrameInfo],
    *,
    err: Exception | None = None,
    package_name: str | None = None,
) -> None:
    """Write the Representation of an Interpreter Stack using a File Object

    Args:
        fp (io.TextIOBase | io.BytesIO): File object to use for writing.
        stack (list[inspect.FrameInfo]): Stack of frames to dump.
        err (Exception | None, optional): Exception that was raised. Defaults to None.
        package_name (str | None, optional): Name of the package to dump from the stack, otherwise non-exclusive if set to None. Defaults to None.
    """
    result = dumps(stack, err=err, package_name=package_name)
    if isinstance(fp, io.BytesIO):
        fp.write((result + "\n").encode("utf-8"))
    else:
        fp.write(result + "\n")


def _dump(
    *,
    stack: list[inspect.FrameInfo],
    err: Exception | None,
    dump_path: str | bytes | os.PathLike | None,
) -> str:
    """Internal Function to Dump the Representation of the Exception and Interpreter Stack to File

    Args:
        stack (list[inspect.FrameInfo]): Stack of frames to dump.
        err (Exception | None): Exception that was raised.
        dump_path (str | bytes | os.PathLike | None): Overridden file path to use for the dump.

    Returns:
        str: Path of the resulting dump.
    """
    msg = dumps(stack, package_name=_global_package_name, err=err) + "\n"
    user_dump_path = dump_path or _global_dump_path
    if user_dump_path is not None:
        # User-provided path (assigned when user ran configure, or overridden in this method)
        with open(_resolve_path(user_dump_path), mode="a", encoding="utf-8") as wf:
            wf.write(msg)
            return wf.name
    else:
        # Temporary file
        with tempfile.NamedTemporaryFile(
            "w",
            # Fix the prefix if the user did not run 'configure'
            prefix=f"{_global_package_name}_stack_and_locals"
            if _global_package_name is not None
            else "stack_and_locals",
            delete=False,
        ) as wf:
            wf.write(msg)
            return wf.name


@contextlib.contextmanager
def dump_on_exception(
    dump_path: str | bytes | os.PathLike | None = None,
) -> Generator[None, None, None]:
    """Content Manager to Dump if an Exception is Raised

    Writes a representation of the exception and trace stack to file.

    Args:
        dump_path (str | bytes | os.PathLike | None, optional): Override the file path to use for the dump. Defaults to None.

    Yields:
        Generator[None, None, None]: Context manager.

    Raises:
        Exception: Exception that was raised.
    """
    try:
        yield
    except Exception as err:
        trace = inspect.trace()
        if len(trace) > 1:
            path = _dump(stack=trace[1:], err=err, dump_path=dump_path)
            _logger.fatal(DUMP_MSG, path=path)

        raise


def _set_levels(logger: logging.Logger, level: int) -> None:
    """Set the Log Level for a Logger and its Handlers

    Args:
        logger (logging.Logger): Logger to set the log level for.
        level (int): Log level to set.
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        _logger.debug(
            "Logger: %s - Setting log level for %s to %d",
            logger.name,
            handler.name,
            level,
        )
        handler.setLevel(level)


def _remove_handlers(logger: logging.Logger) -> None:
    """Remove All Handlers from an Instantiated Logger

    Args:
        logger (logging.Logger): Logger to remove handlers from.
    """
    for handler in logger.handlers:
        _logger.debug("Logger: %s - Removing handler: %s", logger.name, handler.name)
        logger.removeHandler(handler)


def _resolve_path(path: str | bytes | os.PathLike) -> str:
    """Stringify and Resolve Path-Like Objects

    Args:
        path (str | bytes | os.PathLike): Path to resolve.

    Returns:
        str: Resolved path

    Raises:
        TypeError: If the path is not a string, bytes, or path-like object.
    """
    if isinstance(path, bytes):
        path = path.decode("utf-8")
    elif not isinstance(path, str):
        try:
            path = path.__fspath__()
        except AttributeError:
            raise TypeError(f"Object is not path-like: {path!r}")

    # Expand "~" and "~user" constructions
    path = os.path.expanduser(path)

    # Make absolute if not already
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    return path
