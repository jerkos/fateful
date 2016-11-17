import collections
import types

from seito import none
from seito import option
from seito.utils import UHandlerMixin
from seito.underscore import Underscore


class Seq(UHandlerMixin):
    def __init__(self, iterable):
        if not isinstance(iterable, collections.Iterable):
            raise TypeError('seq constructor argument must be an iterable')
        self.sequence = iterable if not isinstance(iterable, collections.Mapping) \
            else iterable.items()
        self.is_gen = isinstance(self.sequence, types.GeneratorType)

    def for_each(self, f, *args, **kwargs):
        for elem in self.sequence:
            self.translate_and_call(elem, f, *args, **kwargs)

    def filter(self, f, *args, **kwargs):
        if self.is_gen:
            return Seq(elem for elem in self.sequence
                       if self.translate_and_call(elem, f, *args, **kwargs))
        return Seq([elem for elem in self.sequence
                    if self.translate_and_call(elem, f, *args, **kwargs)])

    def map(self, f, *args, **kwargs):
        if self.is_gen:
            return Seq(self.translate_and_call(elem, f, *args, **kwargs)
                       for elem in self.sequence)
        return Seq([self.translate_and_call(elem, f, *args, **kwargs)
                    for elem in self.sequence])

    def reduce(self, f):
        v = next(self.sequence) if self.is_gen else self.sequence[0]
        for next_val in self.sequence if self.is_gen else self.sequence[1:]:
            if callable(v) and callable(next_val):
                v = f(v, next_val)
                # v = (Underscore(f) << Underscore(next_val)).f  # f(next_val(x))
            else:
                v = f(v, next_val)
        return v

    def sort(self):
        v = self.ensure_class(self.sequence, list)
        v.sort()
        return Seq(tuple(v))

    def sort_by(self, f, *args, **kwargs):
        v = self.ensure_class(self.sequence, list)
        v.sort(key=lambda x: f.f(x)(*args, **kwargs) if isinstance(f, Underscore) else f)
        return Seq(tuple(v))

    def first_opt(self):
        try:
            return option(next(self.sequence) if self.is_gen else self.sequence[0])
        except (StopIteration, IndexError):
            return none

    def stream(self):
        return self.sequence if self.is_gen else Seq(elem for elem in self.sequence)

    def to_list(self):
        return self.ensure_class(self.sequence, list)

    def to_dict(self):
        return dict(self.sequence)

    def to_set(self):
        return set(self.sequence)


def seq(*args):
    if len(args) == 1 and isinstance(args[0], collections.Iterable):
        return Seq(args[0])
    return Seq(list(args))


def func_and_boolean(f1, f2):
    return lambda x: f1(x) and f2(x)


def func_or_boolean(f1, f2):
    return lambda x: f1(x) or f2(x)

AND_BOOLEAN = func_and_boolean
OR_BOOLEAN = func_or_boolean
