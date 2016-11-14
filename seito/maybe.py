class Maybe(object):
    def __init__(self, v):
        self._is_success = False if isinstance(v, Exception) else True
        self.value = v

    @property
    def is_success(self):
        return self._is_success

    def is_failure(self):
        return not self.is_success

    def get(self):
        if self.is_success:
            return self.value
        raise self.value

    def or_else(self, value):
        if self.is_success:
            return self.value
        return value

    def as_failure(self):
        if not self._is_success:
            yield self.value

    def __repr__(self):
        if self.is_success:
            return 'Success({0})'.format(repr(self.value))
        return 'Failure({0})'.format(repr(self.value))


def _try(f, *args, **kwargs):
    try:
        if callable(f):
            return Maybe(f(*args, **kwargs))
        return Maybe(f)
    except Exception as e:
        return Maybe(e)


