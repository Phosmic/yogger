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