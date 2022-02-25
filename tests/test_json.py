from dataclasses import dataclass
import unittest

from seito.json import parse_as, js, try_parse_as, try_parse_as_opt


@dataclass
class Toto:
    a: str


class Test(unittest.TestCase):
    def test_john_object(self):
        i = js({"z-index": 1000})

        self.assertEqual(i["z-index"].or_else(0), 1000)
        i["toto"] = [1, 2, 3]
        i.toto = [4, 5, 6]
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

        value = parse_as(value, response_class=Toto)
        print(value)

    def test_fail_parse(self):
        value = """[
        {"a": "toto"},
        {"a": "titi"}
      
      """
        res = try_parse_as(value, response_class=Toto)
        print("value: ", value)

        res = try_parse_as_opt(value, response_class=Toto)
