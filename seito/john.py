import json
import collections

from seito.option import none, option, Option
from seito.seq import Seq


def obj(*args):
    return JsObject(*args)


def parse(string, *args, **kwargs):
    return JsObject(json.loads(string, *args, **kwargs))


class JsObject(dict):
    def __init__(self, *args):
        super(JsObject, self).__init__(*args)

    def stringify(self, **kwargs):
        return json.dumps(self, **kwargs)

    def __getitem__(self, item: str) -> Option:
        try:
            v = super(JsObject, self).__getitem__(item)
            if isinstance(v, collections.Iterable):
                return Seq(v)
            return option(v)
        except KeyError:
            return none

    def __getattr__(self, item: str) -> Option:
        try:
            # call get item
            return self[item]
        except KeyError:
            return none

    def __setattr__(self, key, value):
        self[key] = value
