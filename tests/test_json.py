import typing
import unittest
from dataclasses import dataclass
from json import JSONDecodeError

from fateful.container import opt_dict, opt_list
from fateful.json import js_object, parse, try_parse
from fateful.monad.option import Some


@dataclass
class Toto:
    a: str


class Test(unittest.TestCase):
    def test_json_object(self):
        i = opt_dict({"z-index": 1000})

        self.assertEqual(i.maybe("z-index").or_(0), 1000)
        i["toto"] = [1, 2, 3]
        i.toto = [4, 5, 6]
        i.zozo.or_(12)

        str(i)
        self.assertEqual(i.maybe("zindex").or_(0), 0)
        json_obj = opt_dict(a=12, k=13, c={1: 3})
        self.assertEqual(json_obj.a.get(), 12)
        # self.assertEqual(i.toto.map(lambda x: x.to_list()).or_none(), [4, 5, 6])

    def test_stringify(self):
        i = opt_dict({"z-index": 1000})
        self.assertEqual(i.stringify(), """{"z-index":1000}""")

    def test_parse_obj(self):
        value = """[
        {"a": "toto"},
        {"a": "titi"}
      ]
      """

        parse(value)

        value = parse(value, object_hook=Toto)
        print(value)

        value = """{"a": "toto"}"""
        parse(value, object_hook=Toto)
        parse(value)

    def test_fail_parse(self):
        value = """[
        {"a": "toto"},
        {"a": "titi"}

      """
        with self.assertRaises(JSONDecodeError):
            try_parse(value).get()
        with self.assertRaises(JSONDecodeError):
            try_parse(value, object_hook=Toto).get()

    def test_parse_array(self):
        value = """[1, 2, 3, {"a": "12"}]"""
        result: opt_list = typing.cast(opt_list, try_parse(value).get())
        self.assertEqual(result[0], 1)
        self.assertEqual(result[2], 3)
        with self.assertRaises(IndexError):
            result[10]

        self.assertIsInstance(result.at(3), Some)
        print("hello :", result[3], type(result[3]))
        self.assertEqual(result[3].map_to(Toto), Toto(a="12"))
        # performing forwarding

        self.assertEqual(result.at(3).map_to(Toto).get(), Toto(a="12"))

    def test_js_object(self):
        x = js_object({"a": 1, "b": 2, "c": ["1", "2"]})
        y = x.c.get().at(0)
        print(y, type(y))

    def test_js_conv(self):
        x = js_object({"a": 1, "b": 2, "c": ["1", {"a": "2"}]})
        print(x["c"][1], type(x["c"][1]))
        print(type(x))
