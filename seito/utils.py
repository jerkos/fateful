from seito.underscore import Underscore


def is_underscore(x):
    return isinstance(x, Underscore)


def substitute(args, kwargs, elem):
    sa = tuple(elem if is_underscore(y) else y for y in args)
    ka = dict((k, elem) if is_underscore(v) else (k, v) for k, v in kwargs.items())
    return sa, ka
