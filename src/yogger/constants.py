import sys

# NOTE: Support for colors will be added for Windows later.
LOG_FMT = "".join(
    (
        "[ {asctime}.{msecs:04.0f}  ",
        "\33[1m" if sys.platform != "win32" else "",
        "{levelname}",
        "\33[0m" if sys.platform != "win32" else "",
        "  {name} ]  {message}",
    )
)
DATE_FMT = "%Y-%m-%d %H:%M:%S"
DUMP_MSG = "".join(
    (
        "\33[1m" if sys.platform != "win32" else "",
        'Dumped stack and locals to "{path}"',
        "\33[0m" if sys.platform != "win32" else "",
        "\nCopy and paste the following to view:\n    cat '{path}'\n",
    )
)
