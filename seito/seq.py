import random
import string
import collections
import types

from seito.underscore import Underscore

ALPHABET = string.ascii_letters


def get_new_id():
    new_id = ''.join(random.sample(ALPHABET, 20))
    while new_id in locals().keys():
        new_id = ''.join(random.sample(ALPHABET, 20))
    return new_id


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
        return Seq((f(elem, *args, **kwargs) for elem in self.sequence))

    def str_map(self, *args, env, r_var='r'):
        locals().update(env)
        args = list(args)
        if any('=' in x for x in args):
            l = []
            for elem in self.sequence:
                uid = get_new_id()
                locals()[uid] = elem
                args[-1] = 'r=' + args[-1]
                code = ';'.join(a.replace('__', uid) for a in args)
                exec(code) in locals()
                l.append(locals()[r_var])
                del locals()[uid]
            return Seq(l)
        else:
            func = eval('lambda __: ' + args[0])
            return Seq([func(elem) for elem in self])

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
