from seito.utils import UHandlerMixin


class Option(UHandlerMixin):
    def __init__(self, obj, *args, **kwargs):
        self._under = self._get_val(obj, *args, **kwargs)
        self.is_some = self._under is not None
        self.is_nothing = not self.is_some

    def get(self):
        if self.is_nothing:
            raise ValueError("Option is empty")
        return self._under

    def is_empty(self) -> bool:
        return self.is_nothing

    def or_else(self, obj, *args, **kwargs) -> object:
        return self._get_val(obj, *args, **kwargs) if self.is_nothing else self._under

    def or_if_falsy(self, obj, *args, **kwargs) -> object:
        return self._under or self._get_val(obj, *args, **kwargs)

    def or_none(self):
        return self._under or None

    def map(self, func, *args, **kwargs) -> "Option":
        if self.is_some:
            return option(self.translate_and_call(self._under, func, *args, **kwargs))
        return self

    def flat_map(self, func, *args, **kwargs) -> "Option":
        under = self
        while isinstance(under._under, Option):
            under = under._under
        return under.map(func, *args, **kwargs)

    def __iter__(self):
        under = self._under
        while under is not None:
            if isinstance(under, Option):
                under = under._under
            else:
                yield under
                under = None
        # raise StopIteration

    def __getattr__(self, name):
        if self.is_some:
            try:
                attr = getattr(self._under, name)
            except AttributeError:
                print("here")
                return none
            if callable(attr):

                def wrapper(*args, **kwargs):
                    return option(attr(*args, **kwargs))

                return wrapper
            return option(attr)
        return none

    def __call__(self, *args, **kwargs):
        return self

    def __str__(self):
        return f"<Option> {str(self._under)}"

    @staticmethod
    def _get_val(obj, *args, **kwargs):
        if callable(obj):
            try:
                return obj(*args, **kwargs)
            except:
                return None
        return obj


def option(value, *args, **kwargs):
    return Option(value, *args, **kwargs)


def opt_dec(func):
    def wrapper(*args, **kwargs):
        return opt(func, *args, **kwargs)

    return wrapper


# aliases
opt = option
none = option(None)
