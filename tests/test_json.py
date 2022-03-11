from dataclasses import dataclass
import unittest

from seito.json import js, try_parse, parse


@dataclass
class Toto:
    a: str


class Test(unittest.TestCase):
    def test_john_object(self):
        i = js({"z-index": 1000})

        self.assertEqual(i["z-index"].or_else(0), 1000)
        i["toto"] = [1, 2, 3]
        i.toto = [4, 5, 6]
        i.zozo.or_else(12)

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

        resp = parse(value)

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
        res = try_parse(value)

        res = try_parse(value, response_class=Toto)
        print("value: ", value)
