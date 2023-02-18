import collections
import dataclasses

from typing import Any

from .compat import HAS_REQUESTS_PACKAGE

if HAS_REQUESTS_PACKAGE:
    from .compat import (
        Request,
        PreparedRequest,
        Response,
        RequestException,
    )


def pformat(name: str, value: Any) -> str:
    """Formatted Representation of a Variable's Name and Value

    Args:
        name (str): Name of the variable to represent.
        value (Any): Value to represent.
        outer_line_continuation (bool, optional): Whether the outermost representation should be line continued. Defaults to True.

    Returns:
        str: Formatted representation of a variable.
    """
    msg = None
    # Support for Requests package
    if HAS_REQUESTS_PACKAGE:
        if isinstance(value, Response):
            # Requests response
            msg = _requests_response_repr(name, value)
        elif type(value) in (PreparedRequest, Request):
            # Requests request
            msg = _requests_request_repr(name, value)
        elif isinstance(value, RequestException):
            # Requests exception
            msg = _requests_exception_repr(name, value)
        if msg is not None:
            return msg

    if isinstance(value, dict):
        # Dictionary
        msg = _dict_repr(name, value)
    elif isinstance(value, (list, tuple, set, collections.deque)):
        # Container of objects (list, tuple, set, or deque)
        msg = _object_container_repr(name, value)
    elif dataclasses.is_dataclass(value):
        # Dataclass
        msg = _dataclass_repr(name, value)
    if msg is not None:
        return msg

    # Other (also includes string, bytes, ranges, etc.)
    msg = f"{name} = {value!r}"
    # Apply line continuation if contains any newlines
    msg = _apply_line_continuation(msg)
    return msg


def _apply_line_continuation(msg: str) -> str:
    """Prefix with a Backslash and Indent if Contains Any Newlines

    Args:
        msg (str): Representation to apply line continuation to.

    Returns:
        str: String with line continuation and indent applied.
    """
    if "\n" in msg:
        msg = "\\\n  " + msg.replace("\n", "\n  ")
    return msg


if HAS_REQUESTS_PACKAGE:

    def _requests_request_repr(name: str, request: Request) -> str:
        """Representation of a requests.Request Object

        Args:
            name (str): Name of the Requests response.
            request (requests.Request): Request object, prepared by the Requests module.

        Returns:
            str: Formatted representation of a requests.Request object.
        """
        msg = ""
        msg += f"{name} = {request!r}"
        msg += f"\n  {name}.method = {request.method}"
        msg += f"\n  {name}.url = {request.url}"
        msg += f"\n  {name}.headers = "
        if not request.headers:
            # Empty or missing headers
            msg += f"{request.headers!r}"
        else:
            msg += "\\"
            for field in request.headers:
                msg += f'\n    {field} = {pformat("_", request.headers[field])}'

        for attr in ("body", "params", "data"):
            if hasattr(request, attr) and getattr(request, attr):
                msg += f"\n  {name}.{attr} = "
                msg += pformat("_", getattr(request, attr)).replace("\n", "\n  ")
        return msg

    def _requests_response_repr(
        name: str,
        response: Response,
        *,
        include_history: bool = True,
    ) -> str:
        """Representation of a requests.Response Object

        Args:
            name (str): Name of the Requests response.
            response (requests.Response): Response object from the Requests module.
            include_history (bool, optional): Include the request redirect history in the representation (not yet accessable to user). Defaults to True.

        Returns:
            str: Formatted representation of a requests.Response object.
        """
        msg = ""
        msg += f"{name} = {response!r}"
        msg += f"\n  {name}.url = {response.url}"
        msg += f"\n  {name}.request = "
        msg += pformat("_", response.request).replace("\n", "\n  ")
        if include_history and response.history:
            msg += f"\n  {name}.history = ["
            for prev_resp in response.history:
                msg += "\n    "
                msg += _requests_response_repr(
                    "_", prev_resp, include_history=False
                ).replace("\n", "\n    ")

            msg += "\n  ]"

        msg += f"\n  {name}.status_code = {response.status_code}"
        msg += f"\n  {name}.headers = "
        if not response.headers:
            # Empty or missing headers
            msg += f"{response.headers!r}"
        else:
            msg += "\\"
            for field in response.headers:
                msg += f'\n    {field} = {pformat("_", response.headers[field])}'

        msg += f'\n  {name}.content = {pformat("_", response.content)}'
        return msg

    def _requests_exception_repr(name: str, err: RequestException) -> str:
        """Formatted Representation of a requests.exceptions.RequestException

        Args:
            name (str): Name of the Requests Exception.
            err (requests.exceptions.RequestException): Requests exception to represent.

        Returns:
            str: Formatted representation of a Requests exception.
        """
        msg = ""
        msg += f"{name} = {err!r}"
        msg += "\n  " + pformat(f"{name}.request", err.request).replace("\n", "\n  ")
        msg += "\n  " + pformat(f"{name}.response", err.response).replace("\n", "\n  ")
        return msg


def _dict_repr(name: str, value: dict) -> str:
    """Formatted Representation of a Dictionary Variable's Name and Value

    Args:
        name (str): Name of the dict to represent.
        value (dict): Value to represent.

    Returns:
        str: Formatted representation of a dictionary variable.
    """
    msg = ""
    msg += f"{name} = <{type(value).__module__}.{type(value).__name__}>\n  "
    msg += "\n  ".join(
        pformat(f"{name}[{k!r}]", v).replace("\n", "\n  ") for k, v in value.items()
    )
    return msg


def _object_container_repr(
    name: str,
    value: list | tuple | set | collections.deque,
) -> str:
    """Formatted Representation of a Container of Object's Name and Value

    Args:
        name (str): Name of the collection variable to represent.
        value (list | tuple | set | collections.deque): Value to represent.

    Returns:
        str: Formatted representation of a collection variable variable.
    """
    msg = ""
    if all(isinstance(v, (int, str)) for v in value):
        # Single line (all values are int or str)
        msg = f"{name} = {value!r}"
    else:
        # Multiple lines (not all values are int or str)
        msg += f"{name} = <{type(value).__module__}.{type(value).__name__}>\n  "
        msg += "\n  ".join(
            pformat(f"{name}[{i}]", v).replace("\n", "\n  ")
            for i, v in enumerate(value)
        )

    # Apply line continuation if contains any newlines
    msg = _apply_line_continuation(msg)
    return msg


def _dataclass_repr(name: str, value: object) -> str:
    """Formatted Representation of a Dataclass Variable's Name and Value

    Args:
        name (str): Name of the dataclass to represent.
        value (object): Value to represent.

    Returns:
        str: Formatted representation of a dataclass variable.
    """
    msg = ""
    msg += f"{name} = <{type(value).__module__}.{type(value).__name__}>\n  "
    msg += "\n  ".join(
        " = ".join(
            (
                pformat(f"{name}.{f.name}", f.name),
                pformat(f"{name}.{f.name}", getattr(value, f.name)),
            )
        ).replace("\n", "\n  ")
        for f in dataclasses.fields(value)
    )
    return msg
