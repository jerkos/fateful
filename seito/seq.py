import collections
import types

from seito.underscore import Underscore


class Seq(object):
    def __init__(self, iterable, to_stream=False):
        if not isinstance(iterable, collections.Iterable):
            raise TypeError('seq constructor argument must be an iterable')
        self.sequence = iterable if not isinstance(iterable, collections.Mapping) \
            else iterable.items()
        self.to_stream = to_stream
        self.is_gen = isinstance(self.sequence, types.GeneratorType)

    @staticmethod
    def _ensure_callable(f, a, kw):
        return f(*a, **kw) if callable(f) else f

    @staticmethod
    def _ensure_list(elements):
        return elements if isinstance(elements, list) else list(elements)

    @staticmethod
    def _is_underscore(x):
        return isinstance(x, Underscore)

    @staticmethod
    def _substitute(args, kwargs, elem):
        def is_underscore_and_endpoint(x):
            return Seq._is_underscore(x) # and x.is_endpoint
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
        for elem in self.sequence:
            f_, a, kw = self._get_f(elem, f, *args, **kwargs)
            self._ensure_callable(f_, a, kw)

    def filter(self, f, *args, **kwargs):
        def gen():
            for elem in self.sequence:
                f_, a, kw = self._get_f(elem, f, *args, **kwargs)
                if self._ensure_callable(f_, a, kw):
                    yield elem
        return Seq(gen())

    def map(self, f, *args, **kwargs):
        def gen():
            for elem in self.sequence:
                f_, a, kw = self._get_f(elem, f, *args, **kwargs)
                yield self._ensure_callable(f_, a, kw)
        return Seq(gen())

    def sort(self):
        v = self._ensure_list(self.sequence)
        v.sort()
        return Seq(v)

    def sort_by(self, f, *args, **kwargs):
        v = self._ensure_list(self.sequence)
        v.sort(key=lambda x: f.f(x)(*args, **kwargs) if isinstance(f, Underscore) else f)
        return Seq(v)

    def first_opt(self):
        pass

    def stream(self):
        return self.sequence if self._gen else Seq(elem for elem in self.sequence)

    def to_list(self):
        return self._ensure_list(self.sequence)

    def to_dict(self):
        return dict(self.sequence)

    def to_set(self):
        return set(self.sequence)


def seq(*args):
    if len(args) == 1 and isinstance(args[0], collections.Iterable):
        return Seq(args[0])
    return Seq(args)
