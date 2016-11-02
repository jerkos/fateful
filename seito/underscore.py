import operator


def identity(x): return x


def seito_rdy(f):
    return Underscore(lambda *a, **kw: f(*a, **kw))


class Underscore(object):
    def __init__(self, f=identity, args=None, kwargs=None, arity=0, compose=None):
        self.f = f
        self.arity = arity
        self.args = args or []
        self.kwargs = kwargs or {}
        self.compose = compose

    def __getattr__(self, item):
        # f should be identity function a this point
        t = operator.attrgetter(item)

        if item == '_1':
            return Underscore(lambda x: self.f(x[0]), arity=1, compose=(lambda x: self.f(x[0]), [], {}))
        elif item == '_2':
            return Underscore(lambda x: self.f(x[1]), arity=1, compose=(lambda x: self.f(x[1]), [], {}))

        if self.compose is not None:
            f_, args, kwargs = self.compose
            return Underscore(lambda x: t(f_(x)), arity=1, compose=(lambda x: t(f_(x)), args, kwargs))

        return Underscore(lambda x: t(self.f(x)), arity=1,
                          compose=(lambda x: t(self.f(x)), self.args, self.kwargs))

    def apply_f(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        func = lambda x: self.f(x)(*args, **kwargs)
        return Underscore(self.f, args=args, kwargs=kwargs, arity=self.arity, compose=(func, args, kwargs))

    def __add__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) + other
            if callable(self.f(x)) else self.f(x) + other, arity=1
        )

    def __sub__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) - other
            if callable(self.f(x)) else self.f(x) - other, arity=1
        )

    def __mul__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) * other
            if callable(self.f(x)) else self.f(x) * other, arity=1
        )

    def __floordiv__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) // other
            if callable(self.f(x)) else self.f(x) // other, arity=1
        )

    def __truediv__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) / other
            if callable(self.f(x)) else self.f(x) / other, arity=1
        )

    def __pow__(self, power, modulo=None):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) ** power
            if callable(self.f(x)) else self.f(x) ** power, arity=1
        )


underscore = Underscore()
