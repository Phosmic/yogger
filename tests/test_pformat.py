import collections
import dataclasses
import unittest
from itertools import product

import requests

from yogger.pformat import pformat


class PformatTest(unittest.TestCase):
    def test_bytes_wo_newlines(self):
        self.assertEqual(
            pformat("my_variable", b"this is a test"),
            "my_variable = b'this is a test'",
        )

    def test_bytes_w_newlines(self):
        self.assertEqual(
            pformat("my_variable", b"this\nis\na\ntest"),
            "my_variable = b'this\\nis\\na\\ntest'",
        )

    def test_str_wo_newlines(self):
        self.assertEqual(
            pformat("my_variable", "this is a test"),
            "my_variable = 'this is a test'",
        )

    def test_str_w_newlines(self):
        self.assertEqual(
            pformat("my_variable", "this\nis\na\ntest"),
            "my_variable = 'this\\nis\\na\\ntest'",
        )

    def test_set_of_str(self):
        words = {"this", "is", "a", "test"}
        all_combos = filter(
            lambda combo: len(combo) == len(words),
            map(set, product(words, repeat=len(words))),
        )
        # Set order is not guaranteed, so we check all possible combinations
        self.assertRegex(
            pformat("my_variable", words),
            r"^(?:"
            + r"|".join(
                r"(?:my_variable = \{'" + "', '".join(combo) + r"'\})"
                for combo in all_combos
            )
            + r")$",
        )

    def test_set_of_int(self):
        self.assertEqual(
            pformat("my_variable", {0, 1, 2, 3}),
            "my_variable = {0, 1, 2, 3}",
        )

    def test_tuple_of_str(self):
        self.assertEqual(
            pformat("my_variable", ("this", "is", "a", "test")),
            "my_variable = ('this', 'is', 'a', 'test')",
        )

    def test_tuple_of_int(self):
        self.assertEqual(
            pformat("my_variable", (0, 1, 2, 3)),
            "my_variable = (0, 1, 2, 3)",
        )

    def test_tuple_of_str_and_int(self):
        self.assertEqual(
            pformat("my_variable", ("this", 0, "is", 1, "a", 2, "test", 3)),
            "my_variable = ('this', 0, 'is', 1, 'a', 2, 'test', 3)",
        )

    def test_tuple_of_tuple_of_str(self):
        self.assertEqual(
            pformat("my_variable", (("this", "is"), ("a", "test"))),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <builtins.tuple>",
                    "    my_variable[0] = ('this', 'is')",
                    "    my_variable[1] = ('a', 'test')",
                )
            ),
        )

    def test_tuple_of_tuple_of_int(self):
        self.assertEqual(
            pformat("my_variable", ((0, 1), (2, 3))),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <builtins.tuple>",
                    "    my_variable[0] = (0, 1)",
                    "    my_variable[1] = (2, 3)",
                )
            ),
        )

    def test_tuple_of_tuple_of_str_and_int(self):
        self.assertEqual(
            pformat("my_variable", (("this", 0), ("is", 1), ("a", 2), ("test", 3))),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <builtins.tuple>",
                    "    my_variable[0] = ('this', 0)",
                    "    my_variable[1] = ('is', 1)",
                    "    my_variable[2] = ('a', 2)",
                    "    my_variable[3] = ('test', 3)",
                )
            ),
        )

    def test_list_of_str(self):
        self.assertEqual(
            pformat("my_variable", ["this", "is", "a", "test"]),
            "my_variable = ['this', 'is', 'a', 'test']",
        )

    def test_list_of_int(self):
        self.assertEqual(
            pformat("my_variable", [0, 1, 2, 3]),
            "my_variable = [0, 1, 2, 3]",
        )

    def test_list_of_str_and_int(self):
        self.assertEqual(
            pformat("my_variable", ["this", 0, "is", 1, "a", 2, "test", 3]),
            "my_variable = ['this', 0, 'is', 1, 'a', 2, 'test', 3]",
        )

    def test_list_of_list_of_str(self):
        self.assertEqual(
            pformat("my_variable", [["this", "is"], ["a", "test"]]),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <builtins.list>",
                    "    my_variable[0] = ['this', 'is']",
                    "    my_variable[1] = ['a', 'test']",
                )
            ),
        )

    def test_list_of_list_of_int(self):
        self.assertEqual(
            pformat("my_variable", [[0, 1], [2, 3]]),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <builtins.list>",
                    "    my_variable[0] = [0, 1]",
                    "    my_variable[1] = [2, 3]",
                )
            ),
        )

    def test_list_of_list_of_str_and_int(self):
        self.assertEqual(
            pformat("my_variable", [["this", 0], ["is", 1], ["a", 2], ["test", 3]]),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <builtins.list>",
                    "    my_variable[0] = ['this', 0]",
                    "    my_variable[1] = ['is', 1]",
                    "    my_variable[2] = ['a', 2]",
                    "    my_variable[3] = ['test', 3]",
                )
            ),
        )

    def test_deque_of_str(self):
        self.assertEqual(
            pformat("my_variable", collections.deque(["this", "is", "a", "test"])),
            "my_variable = deque(['this', 'is', 'a', 'test'])",
        )

    def test_deque_of_int(self):
        self.assertEqual(
            pformat("my_variable", collections.deque([0, 1, 2, 3])),
            "my_variable = deque([0, 1, 2, 3])",
        )

    def test_deque_of_str_and_int(self):
        self.assertEqual(
            pformat(
                "my_variable",
                collections.deque(["this", 0, "is", 1, "a", 2, "test", 3]),
            ),
            "my_variable = deque(['this', 0, 'is', 1, 'a', 2, 'test', 3])",
        )

    def test_deque_of_deque_of_str(self):
        self.assertEqual(
            pformat(
                "my_variable",
                collections.deque(
                    [
                        collections.deque(["this", "is"]),
                        collections.deque(["a", "test"]),
                    ]
                ),
            ),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <collections.deque>",
                    "    my_variable[0] = deque(['this', 'is'])",
                    "    my_variable[1] = deque(['a', 'test'])",
                )
            ),
        )

    def test_deque_of_deque_of_int(self):
        self.assertEqual(
            pformat(
                "my_variable",
                collections.deque(
                    [
                        collections.deque([0, 1]),
                        collections.deque([2, 3]),
                    ]
                ),
            ),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <collections.deque>",
                    "    my_variable[0] = deque([0, 1])",
                    "    my_variable[1] = deque([2, 3])",
                )
            ),
        )

    def test_deque_of_deque_of_str_and_int(self):
        self.assertEqual(
            pformat(
                "my_variable",
                collections.deque(
                    [
                        collections.deque(["this", 0]),
                        collections.deque(["is", 1]),
                        collections.deque(["a", 2]),
                        collections.deque(["test", 3]),
                    ]
                ),
            ),
            "\n".join(
                (
                    "\\",
                    "  my_variable = <collections.deque>",
                    "    my_variable[0] = deque(['this', 0])",
                    "    my_variable[1] = deque(['is', 1])",
                    "    my_variable[2] = deque(['a', 2])",
                    "    my_variable[3] = deque(['test', 3])",
                )
            ),
        )

    def test_dict_of_str(self):
        self.assertEqual(
            pformat("my_variable", {"first_name": "John", "last_name": "Doe"}),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable['first_name'] = 'John'",
                    "  my_variable['last_name'] = 'Doe'",
                )
            ),
        )

    def test_dict_of_int(self):
        self.assertEqual(
            pformat("my_variable", {0: 1, 2: 3}),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable[0] = 1",
                    "  my_variable[2] = 3",
                )
            ),
        )

    def test_dict_of_str_and_int(self):
        self.assertEqual(
            pformat("my_variable", {"first_name": 0, "last_name": 1}),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable['first_name'] = 0",
                    "  my_variable['last_name'] = 1",
                )
            ),
        )

    def test_dict_of_dict_of_str(self):
        self.assertEqual(
            pformat(
                "my_variable",
                {
                    "name": {"first": "John", "last": "Doe"},
                    "residence": {"city": "New York", "state": "NY"},
                },
            ),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable['name'] = <builtins.dict>",
                    "    my_variable['name']['first'] = 'John'",
                    "    my_variable['name']['last'] = 'Doe'",
                    "  my_variable['residence'] = <builtins.dict>",
                    "    my_variable['residence']['city'] = 'New York'",
                    "    my_variable['residence']['state'] = 'NY'",
                )
            ),
        )

    def test_dict_of_dict_of_int(self):
        self.assertEqual(
            pformat(
                "my_variable",
                {
                    0: {1: 2, 3: 4},
                    5: {6: 7, 8: 9},
                },
            ),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable[0] = <builtins.dict>",
                    "    my_variable[0][1] = 2",
                    "    my_variable[0][3] = 4",
                    "  my_variable[5] = <builtins.dict>",
                    "    my_variable[5][6] = 7",
                    "    my_variable[5][8] = 9",
                )
            ),
        )

    def test_dict_of_list_of_str(self):
        self.assertEqual(
            pformat(
                "my_variable",
                {
                    "names": ["Jane", "John"],
                    "residence": ["NY", "CA"],
                },
            ),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable['names'] = ['Jane', 'John']",
                    "  my_variable['residence'] = ['NY', 'CA']",
                )
            ),
        )

    def test_dict_of_list_of_int(self):
        self.assertEqual(
            pformat("my_variable", {0: [1, 2], 3: [4, 5]}),
            "\n".join(
                (
                    "my_variable = <builtins.dict>",
                    "  my_variable[0] = [1, 2]",
                    "  my_variable[3] = [4, 5]",
                )
            ),
        )

    def test_dataclass(self):
        @dataclasses.dataclass
        class Person:
            name: str
            age: int
            address: str

        self.assertEqual(
            pformat("my_variable", Person("John", 30, "New York")),
            "\n".join(
                (
                    "my_variable = <test_pformat.Person>",
                    "  my_variable.name = 'name' = my_variable.name = 'John'",
                    "  my_variable.age = 'age' = my_variable.age = 30",
                    "  my_variable.address = 'address' = my_variable.address = 'New York'",
                )
            ),
        )

    def test_dataclass_with_nested_dataclass(self):
        @dataclasses.dataclass
        class Address:
            city: str
            state: str

        @dataclasses.dataclass
        class Person:
            name: str
            age: int
            address: Address

        self.assertEqual(
            pformat("my_variable", Person("John", 30, Address("New York", "NY"))),
            "\n".join(
                (
                    "my_variable = <test_pformat.Person>",
                    "  my_variable.name = 'name' = my_variable.name = 'John'",
                    "  my_variable.age = 'age' = my_variable.age = 30",
                    "  my_variable.address = 'address' = my_variable.address = <test_pformat.Address>",
                    "    my_variable.address.city = 'city' = my_variable.address.city = 'New York'",
                    "    my_variable.address.state = 'state' = my_variable.address.state = 'NY'",
                )
            ),
        )

    def test_requests_request(self):
        request = requests.Request(
            method="GET",
            url="https://www.phosmic.com",
            headers={"User-Agent": "Mozilla/5.0"},
            params={"q": "search"},
        )
        self.assertEqual(
            pformat("request", request),
            "\n".join(
                (
                    "request = <Request [GET]>",
                    "  request.method = GET",
                    "  request.url = https://www.phosmic.com",
                    "  request.headers = \\",
                    "    User-Agent = _ = 'Mozilla/5.0'",
                    "  request.params = _ = <builtins.dict>",
                    "    _['q'] = 'search'",
                )
            ),
        )

    def test_requests_request_html(self):
        response = requests.Response()
        response.request = requests.Request()
        response.request.method = "GET"
        response.request.url = "https://phosmic.com/"
        response.request.headers = {
            "User-Agent": "python-requests/2.28.2",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
        }
        response.url = "https://phosmic.com/"
        response.status_code = 200
        response.headers = {
            "Content-Length": "66",
            "Content-Encoding": "gzip",
            "Content-Type": "text/html; charset=utf-8",
        }
        response._content = (
            b'<!DOCTYPE html>\n<html lang="en">\n<body>Phosmic LLC</body>\n</html>\n'
        )
        self.assertEqual(
            pformat("response", response),
            "\n".join(
                (
                    "response = <Response [200]>",
                    "  response.url = https://phosmic.com/",
                    "  response.request = _ = <Request [GET]>",
                    "    _.method = GET",
                    "    _.url = https://phosmic.com/",
                    "    _.headers = \\",
                    "      User-Agent = _ = 'python-requests/2.28.2'",
                    "      Accept-Encoding = _ = 'gzip, deflate'",
                    "      Accept = _ = '*/*'",
                    "  response.status_code = 200",
                    "  response.headers = \\",
                    "    Content-Length = _ = '66'",
                    "    Content-Encoding = _ = 'gzip'",
                    "    Content-Type = _ = 'text/html; charset=utf-8'",
                    "  response.content = _ = b'<!DOCTYPE html>\\n<html lang=\"en\">\\n<body>Phosmic LLC</body>\\n</html>\\n'",
                )
            ),
        )
