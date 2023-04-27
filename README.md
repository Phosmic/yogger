# Yogger

[Yogger](https://github.com/Phosmic/yogger) provides a minimal logging setup with utilities to represent interpreter stacks.

> Supports `requests.Request` and `requests.Response` objects if the **Requests** package is installed.

Example of common usage:

```python
import logging
import yogger

logger = logging.getLogger(__name__)

def main():
    yogger.install()
    yogger.configure(__name__, verbosity=2, dump_locals=True)
    with yogger.dump_on_exception():
        # Code goes here

if __name__ == "__main__":
    main()
```

---

## Requirements:

**Yogger** requires Python 3.10 or higher, is platform independent, and has no outside dependencies.

## Issue reporting

If you discover an issue with Yogger, please report it at [https://github.com/Phosmic/yogger/issues](https://github.com/Phosmic/yogger/issues).

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

---

-   [Requirements](#requirements)
-   [Installing](#installing)
-   [Usage](#usage)
-   [Library](#library)

## Installing

Most stable version from [**PyPi**](https://pypi.org/project/yogger/):

[![PyPI](https://img.shields.io/pypi/v/yogger?style=flat-square)](https://pypi.org/project/yogger/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/yogger?style=flat-square)](https://pypi.org/project/yogger/)
[![PyPI - License](https://img.shields.io/pypi/l/yogger?style=flat-square)](https://pypi.org/project/yogger/)

```bash
python3 -m pip install yogger
```

Development version from [**GitHub**](https://github.com/Phosmic/yogger):


![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Phosmic/yogger/ubuntu.yml?style=flat-square)
![Codecov](https://img.shields.io/codecov/c/github/Phosmic/yogger/master?flag=unittests&style=flat-square&token=XMJZIW8ZL3)
![GitHub](https://img.shields.io/github/license/Phosmic/yogger?style=flat-square)


```bash
git clone git+https://github.com/Phosmic/yogger.git
cd yogger
python3 -m pip install -e .
```

---

## Usage

Import packages and instantiate a logger:

```python
import logging
import yogger

logger = logging.getLogger(__name__)
```

Install the logger class and configure with your package name:

> Place at the start of the top-level function.

```python
def main():
    yogger.install()
    yogger.configure(__name__)
    # Code goes here
```

### Output

Example of logger output:

<pre><code>[ 2023-01-17 10:16:09.0918  <b>INFO</b>  my_package ]  Something we want to log.
[ 2023-01-17 10:16:09.0918  <b>DEBUG</b>  my_package ]  Something we want to log.
[ 2023-01-17 10:16:09.0918  <b>WARNING</b>  my_package ]  Something we want to log.
[ 2023-01-17 10:16:09.0918  <b>ERROR</b>  my_package ]  Something we want to log.`
[ 2023-01-17 10:16:09.0918  <b>CRITICAL</b>  my_package ]  Something we want to log.</code></pre>

> Note: Support for rich text has not yet been added for Windows platforms.

## Support for dumping the stack

### Traces and exceptions

Using the `dump_on_exception` **context manager** dumps the exception and trace if an exception is raised:

```python
with yogger.dump_on_exception(
    # Uncomment to override
    # dump_path="./stack_dump.txt",
):
    raise SomeException
```

This is nearly equivalent to:

```python
import inspect
```

```python
try:
    raise SomeException
except Exception as e:
    trace = inspect.trace()
    if len(trace) > 1:
        with open("./stack_dump.txt", mode="a", encoding="utf-8") as f:
            yogger.dump(f, trace[1:], e=e, package_name="my_package")
```

### Stacks

Setting `dump_locals=True` when running `yogger.configure` dumps a representation of the caller's stack upon logging with a level of warning or higher.

To manually dump the stack, something like this would suffice:

```python
import inspect
```

```python
stack = inspect.stack()
if len(stack) > 2:
    with open("./example.log", mode="w", encoding="utf-8") as f:
        yogger.dump(f, stack[2:][::-1])
```

If you simply want the string representation, use the `yogger.dumps` function:

```python
stack = inspect.stack()
if len(stack) > 2:
    trace_repr = yogger.dumps(stack[2:][::-1])
```

### Output

Example of dictionary representation in dump:

```python
example = {
    "user_id": 123456790,
    "profile": {
        "name": "John Doe",
        "birthdate": datetime.date(2000, 1, 1),
        "weight_kg": 86.18,
    },
    "video_ids": [123, 456, 789],
}
```

```text
example = <builtins.dict>
  example['user_id'] = 123456790
  example['profile'] = <builtins.dict>
    example['profile']['name'] = 'John Doe'
    example['profile']['birthdate'] = datetime.date(2000, 1, 1)
    example['profile']['weight_kg'] = 86.18
  example['video_ids'] = [123, 456, 789]
```

Similarly for a dataclass:

```python
@dataclasses.dataclass
class Example:
    user_id: int
    profile: dict[str, str | float | datetime.date]
    video_ids: list[int]
```

```text
example = <my_package.Example>
  example.user_id = 'user_id' = example.user_id = 123456790
  example.profile = 'profile' = example.profile = <builtins.dict>
    example.profile['name'] = 'John Doe'
    example.profile['birthdate'] = datetime.date(2000, 1, 1)
    example.profile['weight_kg'] = 86.18
  example.video_ids = 'video_ids' = example.video_ids = [123, 456, 789]
```

---

## Library

### About the `package_name` parameter

The `package_name` parameter gives Yogger an idea of what belongs to your application. This name is used to identify which frames to dump in the stack. So it’s important what you provide there. If you are using a single module, `__name__` is always the correct value. If you are using a package, it’s usually recommended to hardcode the name of your package there.

For example, if your application is defined in "my_package/app.py", you should create it with one of the two versions below:

```python
yogger.configure("my_package")
```

```python
yogger.configure(__name__.split(".")[0])
```

Why is that? The application will work even with `__name__`, thanks to how resources are looked up. However, it will make debugging more painful. Yogger makes assumptions based on the import name of your application. If the import name is not properly set up, that debugging information may be lost.

<a id="yogger.pformat"></a>

# `yogger.pformat`

Create a formatted representation of a variable's name and value.

This module is used to create a formatted representation of a variable's name and value.

<a id="yogger.pformat.pformat"></a>

#### `pformat`

```python
def pformat(name: str,
            value: Any,
            outer_line_continuation: bool = True) -> str
```

Create a formatted representation of a variable's name and value.

**Arguments**:

- `name` _str_ - Name of the variable to represent.
- `value` _Any_ - Value to represent.
- `outer_line_continuation` _bool, optional_ - Whether the outermost representation should be line continued. Defaults to True.

**Returns**:

- _str_ - Formatted representation of a variable's name and value.

<a id="yogger.base"></a>

# `yogger.base`

Yogger Base Module

This module contains the base classes and functions for Yogger.

<a id="yogger.base.Yogger"></a>

## `Yogger` Objects

```python
class Yogger(logging.Logger)
```

Yogger Logger Class

This class is used to override the default `logging.Logger` class.

<a id="yogger.base.install"></a>

#### `install`

```python
def install() -> None
```

Install the Yogger Logger Class and Instantiate the Global Logger

<a id="yogger.base.configure"></a>

#### `configure`

```python
def configure(package_name: str,
              *,
              verbosity: int = 0,
              dump_locals: bool = False,
              dump_path: str | bytes | os.PathLike | None = None,
              remove_handlers: bool = True) -> None
```

Prepare for Logging

**Arguments**:

- `package_name` _str_ - Name of the package to dump from the stack.
- `verbosity` _int, optional_ - Level of verbosity (0-2) for log messages. Defaults to 0.
- `dump_locals` _bool, optional_ - Dump the caller's stack when logging with a level of warning or higher. Defaults to False.
- `dump_path` _str | bytes | os.PathLike, optional_ - Custom path to use when dumping with 'dump_on_exception' or when 'dump_locals=True', otherwise use a temporary path if None. Defaults to None.
- `remove_handlers` _bool, optional_ - Remove existing logging handlers before adding the new stream handler. Defaults to True.

<a id="yogger.base.dumps"></a>

#### `dumps`

```python
def dumps(stack: list[inspect.FrameInfo],
          *,
          err: Exception | None = None,
          package_name: str | None = None) -> str
```

Create a String Representation of an Interpreter Stack

Externalizes '_stack_dumps' to be accessed by the user.

**Arguments**:

- `stack` _list[inspect.FrameInfo]_ - Stack of frames to represent.
- `err` _Exception | None, optional_ - Exception that was raised. Defaults to None.
- `package_name` _str | None, optional_ - Name of the package to dump from the stack, otherwise non-exclusive if set to None. Defaults to None.

**Returns**:

- _str_ - Representation of the stack.

<a id="yogger.base.dump"></a>

#### `dump`

```python
def dump(fp: io.TextIOBase | io.BytesIO,
         stack: list[inspect.FrameInfo],
         *,
         err: Exception | None = None,
         package_name: str | None = None) -> None
```

Write the Representation of an Interpreter Stack using a File Object

**Arguments**:

- `fp` _io.TextIOBase | io.BytesIO_ - File object to use for writing.
- `stack` _list[inspect.FrameInfo]_ - Stack of frames to dump.
- `err` _Exception | None, optional_ - Exception that was raised. Defaults to None.
- `package_name` _str | None, optional_ - Name of the package to dump from the stack, otherwise non-exclusive if set to None. Defaults to None.

<a id="yogger.base.dump_on_exception"></a>

#### `dump_on_exception`

```python
@contextlib.contextmanager
def dump_on_exception(
    dump_path: str | bytes | os.PathLike | None = None
) -> Generator[None, None, None]
```

Content Manager to Dump if an Exception is Raised

Writes a representation of the exception and trace stack to file.

**Arguments**:

- `dump_path` _str | bytes | os.PathLike | None, optional_ - Override the file path to use for the dump. Defaults to None.

**Yields**:

- _Generator[None, None, None]_ - Context manager.

**Raises**:

- `Exception` - Exception that was raised.


---

