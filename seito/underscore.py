import operator


def identity(x): return x


def seito_rdy(f):
    return Underscore(lambda *a, **kw: f(*a, **kw))


class Underscore(object):
    def __init__(self, f=identity, args=None, kwargs=None, arity=0, compose=None, is_endpoint=False):
        self.f = f
        self.arity = arity
        self.args = args or []
        self.kwargs = kwargs or {}
        self.compose = compose
        self.is_endpoint = is_endpoint

    def __getattr__(self, item):
        # f should be identity function a this point
        t = operator.attrgetter(item)
        if item == '_1':
            return Underscore(lambda x: self.f(x[0]), arity=1, compose=self.f, is_endpoint=True)
        elif item == '_2':
            return Underscore(lambda x: self.f(x[1]), arity=1, compose=self.f, is_endpoint=True)

        if self.compose is not None:
            return Underscore(lambda x: t(self.f(self.compose(x))), arity=1)
        return Underscore(lambda x: t(self.f(x)), arity=1)

    def apply_f(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return Underscore(self.f, args, kwargs, self.arity)

    def __add__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs)
            if callable(self.f(x)) else self.f(x) + other, arity=1, is_endpoint=True
        )

    def __sub__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs)
            if callable(self.f(x)) else self.f(x) - other, arity=1, is_endpoint=True
        )

    def __mul__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs)
            if callable(self.f(x)) else self.f(x) * other, arity=1, is_endpoint=True
        )

    def __floordiv__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs)
            if callable(self.f(x)) else self.f(x) // other, arity=1, is_endpoint=True
        )

    def __truediv__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs)
            if callable(self.f(x)) else self.f(x) / other, arity=1, is_endpoint=True
        )

    def __pow__(self, power, modulo=None):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs)
            if callable(self.f(x)) else self.f(x) ** power, arity=1, is_endpoint=True
        )


underscore = Underscore()
