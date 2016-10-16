import collections
import types

from seito.underscore import Underscore


class Seq(object):
    def __init__(self, iterable):
        if not isinstance(iterable, collections.Iterable):
            raise TypeError('seq constructor argument must be an iterable')
        self.sequence = iterable

    def for_each(self, f, *args, **kwargs):
        for elem in self.sequence:
            f(elem, *args, **kwargs)

    def filter(self, f, *args, **kwargs):
        return Seq([elem for elem in self.sequence if f(elem, *args, **kwargs)])

    def map(self, f, *args, **kwargs):
        if isinstance(f, Underscore):
            f = f.f
        return seq((f(elem, *args, **kwargs) for elem in self.sequence))

    def stream(self):
        if isinstance(self.sequence, types.GeneratorType):
            return self.sequence
        return seq((elem for elem in self.sequence))

    def to_list(self):
        return list(self.sequence)


def seq(*args):
    if len(args) == 1 and isinstance(args[0], collections.Iterable):
        return Seq(args[0])
    return Seq(args)
