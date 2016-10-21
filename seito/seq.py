import collections
import types

from seito.underscore import Underscore, Tuple1, Tuple2


class Seq(object):
    def __init__(self, iterable):
        if not isinstance(iterable, collections.Iterable):
            raise TypeError('seq constructor argument must be an iterable')
        self.sequence = iterable
        self._is_mapping_type = isinstance(iterable, collections.Mapping)

    def _get_elements(self):
        if self._is_mapping_type:
            return self.sequence.items()
        return self.sequence

    @staticmethod
    def _is_underscore(x):
        return isinstance(x, Underscore)

    @staticmethod
    def _substitute(args, kwargs, elem):
        # replace underscore
        #sa = tuple(elem if Seq._is_underscore(y) else y for y in args)
        #ka = dict((k, elem) if Seq._is_underscore(v) else (k, v) for k, v in kwargs.items())
        #return sa, ka
        # replace tuplevalue
        sa_t = []
        for a in args:
            if Seq._is_underscore(a) and a.is_endpoint:
                sa_t.append(a.apply_f(elem))
            else:
                sa_t.append(elem)
        ka_t = {}
        for (k, v) in kwargs.items():
            if Seq._is_underscore(v) and v.is_endpoint:
                ka_t[k] = v.apply_f(elem)
            else:
                ka_t[k] = elem
        return tuple(sa_t), ka_t

    def for_each(self, f, *args, **kwargs):
        if len(args) > 1:
            # first is the function to call
            # others the arguments needed
            for elem in self._get_elements():
                a, kw = self._substitute(args, kwargs, elem)
                f(*a, **kw)
        elif len(args) == 1:
            # only args maybe an underscore class or simple value
            v = args[0]
            for elem in self._get_elements():
                f(elem) if self._is_underscore(v) else f(elem, v)
        else:
            # no args provided
            # basically 2 cases
            for elem in self._get_elements():
                if isinstance(f, Underscore):
                    if f.arity == 1:
                        # lambda applying on elem
                        f.apply_f(elem)(*f.args, **f.kwargs)
                    else:
                        # retrieving args and kwargs passed
                        if f.args or f.kwargs:
                            a, kw = self._substitute(f.args, f.kwargs, elem)
                            f.apply_f(*a, **kw)
                else:
                    # no argument supplied, simplest case
                    # apply to f to element
                    f(elem)

    def filter(self, f, *args, **kwargs):
        return Seq([elem for elem in self.sequence if f(elem, *args, **kwargs)])

    def map(self, f, *args, **kwargs):
        if isinstance(f, Underscore):
            f = f.f
        return Seq((f(elem, *args, **kwargs) for elem in self.sequence))

    def stream(self):
        if isinstance(self.sequence, types.GeneratorType):
            return self.sequence
        return Seq((elem for elem in self.sequence))

    def to_list(self):
        return list(self.sequence)


def seq(*args):
    if len(args) == 1 and isinstance(args[0], collections.Iterable):
        return Seq(args[0])
    return Seq(args)
