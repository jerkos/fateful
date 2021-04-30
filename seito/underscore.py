import operator


def identity(x): return x


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
        return Underscore(lambda: self.f(*args, **kwargs), args=args, kwargs=kwargs, arity=self.arity) # compose=(func, args, kwargs))
        # return Underscore(self.f, args=args, kwargs=kwargs, arity=self.arity, compose=(func, args, kwargs))

    def __add__(self, other):
        func = (lambda x: self.f(x)(*self.args, **self.kwargs) + other
            if callable(self.f(x)) else self.f(x) + other)
        
        if isinstance(other, Underscore):
            print('hello')
            func = lambda x: self.f(x)(*self.args, **self.kwargs) + other.f(x)(*self.args, **self.kwargs)
        return Underscore(
            func, arity=1
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

    def __gt__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) > other
            if callable(self.f(x)) else self.f(x) > other, arity=1
        )

    def __lt__(self, other):
        return Underscore(
            lambda x: self.f(x)(*self.args, **self.kwargs) < other
            if callable(self.f(x)) else self.f(x) < other, arity=1
        )

    def __lshift__(self, other):
        return Underscore(lambda *args, **kwargs: self.f(other(*args, **kwargs)))

    
    def lift(self, func):
        value = Underscore(lambda *args, **kwargs: func(self.f(*args, **kwargs)))
        return value
        
    def end(self):
      return self.f


def seito_rdy(f):
    return Underscore(lambda *a, **kw: f(*a, **kw))

F = seito_rdy

underscore = Underscore()
