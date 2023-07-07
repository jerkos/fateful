import typing
import unittest
from dataclasses import dataclass
from json import JSONDecodeError

from seito.json import JsArray, JsObject, js, parse, try_parse


@dataclass
class Toto:
    a: str


class Test(unittest.TestCase):
    def test_john_object(self):
        i = js({"z-index": 1000})

        self.assertEqual(i["z-index"].or_else(0), 1000)
        i["toto"] = [1, 2, 3]
        i.toto = [4, 5, 6]
        i.zozo.or_(12)

        str(i)
        self.assertEqual(i["zindex"].or_else(0), 0)
        json_obj = js(a=12, k=13, c={1: 3})
        self.assertEqual(json_obj.a.get(), 12)
        # self.assertEqual(i.toto.map(lambda x: x.to_list()).or_none(), [4, 5, 6])

    def test_stringify(self):
        i = js({"z-index": 1000})
        self.assertEqual(i.stringify(sort_keys=True), """{"z-index": 1000}""")

    def test_parse_obj(self):
        value = """[
        {"a": "toto"},
        {"a": "titi"}
      ]
      """

        parse(value)

        value = parse(value, response_class=Toto)
        print(value)

        value = """{"a": "toto"}"""
        parse(value, response_class=Toto)
        parse(value)

    def test_fail_parse(self):
        value = """[
        {"a": "toto"},
        {"a": "titi"}

      """
        with self.assertRaises(JSONDecodeError):
            try_parse(value).get()
        with self.assertRaises(JSONDecodeError):
            try_parse(value, response_class=Toto).get()

    def test_parse_array(self):
        value = """[1, 2, 3, {"a": "12"}]"""
        result: JsArray = typing.cast(JsArray, try_parse(value).get())
        self.assertEqual(result[0], 1)
        self.assertEqual(result[2], 3)
        with self.assertRaises(IndexError):
            result[10]

        self.assertIsInstance(result[3], JsObject)
        self.assertEqual(result[3].map_to(Toto), Toto(a="12"))
