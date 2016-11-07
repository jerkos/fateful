from seito.utils import UHandlerMixin


class Option(UHandlerMixin):
    def __init__(self, obj, *args, **kwargs):
        self.__under = self.__get_val(obj, *args, **kwargs)
        self.is_some = self.__under is not None
        self.is_nothing = not self.is_some

    def get(self):
        if self.is_nothing:
            raise ValueError('Option is empty')
        return self.__under

    def is_empty(self) -> bool:
        return self.is_nothing

    def or_else(self, obj, *args, **kwargs) -> object:
        value = self.__get_val(obj, *args, **kwargs)
        if self.is_nothing:
            return value
        return self.__under

    def or_if_false(self, obj, *args, **kwargs) -> object:
        value = self.__get_val(obj, *args, **kwargs)
        return self.__under or value

    def or_none(self):
        return self.__under or None

    def map(self, func, *args, **kwargs) -> 'Option':
        if self.is_some:
            return option(self.translate_and_call(
                self.__under, func, *args, **kwargs)
            )
        return self

    def __iter__(self):
        under = self.__under
        while under is not None:
            if isinstance(under, Option):
                under = under.__under
            else:
                yield under
                under = None
        raise StopIteration

    def __getattr__(self, name):
        if self.is_some:
            try:
                attr = getattr(self.__under, name)
            except AttributeError:
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
        return '<Option> {}'.format(str(self.__under))

    @staticmethod
    def __get_val(obj, *args, **kwargs):
        if callable(obj):
            return obj(*args, **kwargs)
        return obj


def option(value):
    return Option(value)


# aliases
opt = option
none = option(None)
