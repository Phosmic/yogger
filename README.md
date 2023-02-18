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

## Requirements:

**Yogger** requires Python 3.10 or higher, is platform independent, and has no outside dependencies.

## Issue reporting

If you discover an issue with Yogger, please report it at [https://github.com/Phosmic/yogger/issues](https://github.com/Phosmic/yogger/issues).

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

---

## Installing

Most stable version from [**PyPi**](https://pypi.org/project/yogger/):

```bash
python3 -m pip install yogger
```

Development version from [**GitHub**](https://github.com/Phosmic/yogger):

```bash
git clone git+https://github.com/Phosmic/yogger.git
cd yogger
python3 -m pip install -e .
```

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
    with open("./example.log", mode="w", encoding="utf-8") as fp:
        yogger.dump(fp, stack[2:][::-1])
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

### yogger.install

Function to install the logger class and instantiate the global logger.

| Function Signature |
| :----------------- |
| install()          |

| Parameters |
| :--------- |
| Empty      |

### yogger.configure

Function to prepare for logging.

| Function Signature                                                                                |
| :------------------------------------------------------------------------------------------------ |
| configure(package_name, \*, verbosity=0, dump_locals=False, dump_path=None, remove_handlers=True) |

| Parameters                                           |                                                                                                                              |
| :--------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| **package_name**_(str)_                              | Name of the package to dump from the stack.                                                                                  |
| **verbosity**_(int)_                                 | Level of verbosity (0-2) for log messages.                                                                                   |
| **dump_locals**_(bool)_                              | Dump the caller's stack when logging with a level of warning or higher.                                                      |
| **dump_path**_(str \| bytes \| os.PathLike \| None)_ | Custom path to use when dumping with `dump_on_exception` or when `dump_locals=True`, otherwise use a temporary path if None. |
| **remove_handlers**_(bool)_                          | Remove existing logging handlers before adding the new stream handler.                                                       |

### yogger.dump_on_exception

Context manager to dump a representation of the exception and trace stack to file if an exception is raised.

| Function Signature                |
| :-------------------------------- |
| dump_on_exception(dump_path=None) |

| Parameters                                           |                                             |
| :--------------------------------------------------- | :------------------------------------------ |
| **dump_path**_(str \| bytes \| os.PathLike \| None)_ | Override the file path to use for the dump. |

### yogger.dump

Function to write the representation of an interpreter stack using a file object.

| Function Signature                             |
| :--------------------------------------------- |
| dump(fp, stack, \*, e=None, package_name=None) |

| Parameters                            |                                                                                     |
| :------------------------------------ | :---------------------------------------------------------------------------------- |
| **fp**_(io.TextIOBase \| io.BytesIO)_ | File object to use for writing.                                                     |
| **stack**_(list[inspect.FrameInfo])_  | Stack of frames to dump.                                                            |
| **e**_(Exception \| None)_            | Exception that was raised.                                                          |
| **package_name**_(str \| None)_       | Name of the package to dump from the stack, otherwise non-exclusive if set to None. |

### yogger.dumps

Function to create a string representation of an interpreter stack.

| Function Signature                          |
| :------------------------------------------ |
| dumps(stack, \*, e=None, package_name=None) |

| Parameters                           |                                                                                     |
| :----------------------------------- | :---------------------------------------------------------------------------------- |
| **stack**_(list[inspect.FrameInfo])_ | Stack of frames to represent.                                                       |
| **e**_(Exception \| None)_           | Exception that was raised.                                                          |
| **package_name**_(str \| None)_      | Name of the package to dump from the stack, otherwise non-exclusive if set to None. |

### yogger.pformat

Function to create a string representation of a variable's name and value.

| Function Signature   |
| :------------------- |
| pformat(name, value) |

| Parameters       |                                    |
| :--------------- | :--------------------------------- |
| **name**_(str)_  | Name of the variable to represent. |
| **value**_(str)_ | Value to represent.                |