import operator


def identity(x): return x


class Underscore(object):
    def __init__(self, f=identity):
        self.f = f

    def __getattr__(self, item):
        # f should be identity function a this point
        t = operator.attrgetter(item)
        return Underscore(lambda x: t(self.f(x)))

    def apply_f(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return Underscore(lambda x, *ag, **kw: self.f(x)(*args, **kwargs))

    def __add__(self, other):
        return Underscore(lambda x, *ag, **kw: self.f(x, *ag, **kw) + other)

    def __sub__(self, other):
        return Underscore(lambda x, *ag, **kw: self.f(x, *ag, **kw) - other)

    def __mul__(self, other):
        return Underscore(lambda x, *ag, **kw: self.f(x, *ag, **kw) * other)

    def __floordiv__(self, other):
        return Underscore(lambda x, *ag, **kw: self.f(x, *ag, **kw) // other)

    def __truediv__(self, other):
        return Underscore(lambda x, *ag, **kw: self.f(x, *ag, **kw) / other)

    def __pow__(self, power, modulo=None):
        return Underscore(lambda x, *ag, **kw: self.f(x, *ag, **kw) ** power)


underscore = Underscore()
