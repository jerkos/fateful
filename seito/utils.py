import collections

from seito.underscore import Underscore


class UHandlerMixin(object):
    """
    Mixin to handle Underscore management instead of lambda
    """

    @staticmethod
    def ensure_callable(f, a, kw):
        return f(*a, **kw) if callable(f) else f

    @staticmethod
    def ensure_class(elements, clazz):
        return elements if isinstance(elements, clazz) else clazz(elements)

    @staticmethod
    def is_underscore(x):
        return isinstance(x, Underscore)

    @staticmethod
    def substitute(args, kwargs, elem):
        sa = []
        skw = {}

        is_underscore = UHandlerMixin.is_underscore

        def arg_unit_handle(x, y):
            if is_underscore(x):
                sa.append(x.apply_f(y))
            elif isinstance(x, collections.Iterable):
                sa.append(tuple(i.apply_f(elem) if is_underscore(i) else elem
                                for i in x))
            else:
                sa.append(y)

        def kwarg_unit_handle(k, x, y):
            if is_underscore(x):
                skw[k] = x.apply_f(y)
            elif isinstance(kwargs[k], collections.Iterable):
                skw[k] = tuple(i.apply_f(elem) if is_underscore(i) else elem
                               for i in x)
            else:
                skw[k] = y

        for arg in args:
            arg_unit_handle(arg, elem)

        for (key, value) in kwargs.items():
            kwarg_unit_handle(key, value, elem)

        return sa, skw

    @staticmethod
    def get_f(elem, f, *args, **kwargs):
        if len(args) > 1:
            # first is the function to call
            # others the arguments needed
            a, kw = UHandlerMixin.substitute(args, kwargs, elem)
            return f, a, kw
        elif len(args) == 1:
            # only args maybe an underscore class or simple value
            v = args[0]
            return (f, (elem,), {}) if UHandlerMixin.is_underscore(v) else (f, (elem, v), {})
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
                    a, kw = UHandlerMixin.substitute(f.args, f.kwargs, elem)
                    return f.apply_f, a, kw
            else:
                # no argument supplied, simplest case
                # apply to f to element
                return f, (elem,), {}

    @staticmethod
    def translate_and_call(elem, f, *args, **kwargs):
        return UHandlerMixin.ensure_callable(*UHandlerMixin.get_f(elem, f, *args, **kwargs))
