import collections
import types

from seito.underscore import Underscore


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
        def is_underscore_and_endpoint(x):
            return Seq._is_underscore(x) and x.is_endpoint
        sa = []
        skw = {}

        def arg_unit_handle(x, y):
            if is_underscore_and_endpoint(x):
                sa.append(x.apply_f(y))
            elif isinstance(x, collections.Iterable):
                sa.append(tuple(i.apply_f(elem) if is_underscore_and_endpoint(i) else elem
                                for i in x))
            else:
                sa.append(y)

        def kwarg_unit_handle(k, x, y):
            if is_underscore_and_endpoint(x):
                skw[k] = x.apply_f(y)
            elif isinstance(kwargs[k], collections.Iterable):
                skw[k] = tuple(i.apply_f(elem) if is_underscore_and_endpoint(i) else elem
                               for i in x)
            else:
                skw[k] = y

        for arg in args:
            arg_unit_handle(arg, elem)

        for (key, value) in kwargs.items():
            kwarg_unit_handle(key, value, elem)

        return sa, skw
        # sa_t = tuple(a.apply_f(elem) if is_underscore_and_endpoint(a) else elem
        #              for a in args)
        # ka_t = dict((k, v.apply_f(elem)) if is_underscore_and_endpoint(v) else (k, elem)
        #             for (k, v) in kwargs.items())
        # return sa_t, ka_t

    def _get_f(self, elem, f, *args, **kwargs):
        if len(args) > 1:
            # first is the function to call
            # others the arguments needed
            a, kw = self._substitute(args, kwargs, elem)
            return f, a, kw
        elif len(args) == 1:
            # only args maybe an underscore class or simple value
            v = args[0]
            return (f, (elem,), {}) if self._is_underscore(v) else (f, (elem, v), {})
        else:
            # no args provided
            # basically 2 cases
            if isinstance(f, Underscore):
                if f.arity == 1:
                    # lambda applying on elem
                    return f.apply_f(elem), f.args, f.kwargs
                else:
                    # retrieving args and kwargs passed
                    # if f.args or f.kwargs:
                    a, kw = self._substitute(f.args, f.kwargs, elem)
                    return f.apply_f, a, kw
            else:
                # no argument supplied, simplest case
                # apply to f to element
                return f, (elem,), {}

    def for_each(self, f, *args, **kwargs):
        for elem in self._get_elements():
            f_, a, kw = self._get_f(elem, f, *args, **kwargs)
            f_(*a, **kw)

    def filter(self, f, *args, **kwargs):
        def gen():
            for elem in self._get_elements():
                f_, a, kw = self._get_f(elem, f, *args, **kwargs)
                if f_(*a, **kw):
                    yield elem
        return Seq(gen())

    def map(self, f, *args, **kwargs):
        def gen():
            for elem in self._get_elements():
                f_, a, kw = self._get_f(elem, f, *args, **kwargs)
                yield f_(*a, **kw)
        return Seq(gen())

    def stream(self):
        if isinstance(self.sequence, types.GeneratorType):
            return self.sequence
        return Seq((elem for elem in self.sequence))

    def to_list(self):
        return list(self._get_elements())

    def to_dict(self):
        #  sa = [self._get_elements()]
        return dict(self._get_elements())


def seq(*args):
    if len(args) == 1 and isinstance(args[0], collections.Iterable):
        return Seq(args[0])
    return Seq(args)
