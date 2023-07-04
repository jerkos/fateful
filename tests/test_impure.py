import random

from seito.monad.effect import Effect, lift_effect


def test_impure():
    Effect(random.randint(1, 2)).map(lambda val: print(val))

    def read_file() -> Effect[list[str]]:
        with open("pyproject.toml", "r") as f:
            return Effect(f.readlines())

    read_file().map(lambda lines: print(lines[0]))

    @lift_effect
    def read_file_raw() -> list[str]:
        with open("pyproject.toml", "r") as f:
            return f.readlines()

    read_file_raw().map(lambda lines: print(lines[1]))
