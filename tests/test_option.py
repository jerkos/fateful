import unittest
from functools import partial

from loguru import logger

from seito.http import HttpException
from seito.monad.func import identity, raise_error, raise_err
from seito.monad.opt import (
    option,
    none,
    opt,
    EmptyError,
    Err,
    Some,
    Empty,
    opt_from_call,
    when,
    MatchError,
    default,
    err,
)
from fn import _
from seito.monad.opt import _ as __


class A:
    def __init__(self, x):
        self.x = x


class Test(unittest.TestCase):
    def test_option_none_get(self):
        with self.assertRaises(EmptyError):
            r = none.get()

    def test_option_is_empty(self):
        self.assertTrue(none.is_empty())
        value = "hello world"
        self.assertFalse(option(value).is_empty())

    def test_option_or_else(self):
        value = 1
        self.assertEqual(none.or_else(value), 1)
        self.assertEqual(none.or_else(lambda: 1), 1)
        self.assertEqual(option(value).map(lambda v: v + 1).or_else(0), 2)

    def test_option_map(self):
        none_value = None
        one_value = 1
        with self.assertRaises(ValueError):
            option(none_value).map(lambda v: v + 1).get()
        self.assertEqual(option(none_value).map(lambda v: v + 1).or_else(2), 2)
        self.assertEqual(option(one_value).map(lambda v: v + 1).get(), 2)
        self.assertEqual(option(one_value).map(_ + 1).get(), 2)

        uppercase = "VALUE"
        self.assertEqual(
            option(uppercase).map(lambda value: value.lower()).or_else(""), "value"
        )

    def test_option_iteration(self):
        value = 1
        for v in option(value):
            self.assertEqual(v, 1)
        self.assertEqual(list(opt(None)), [])

    def test_option_forwarding(self):
        value = "VALUE"
        self.assertEqual(option(value).lower().or_else(""), "value")
        self.assertEqual(none.lower().or_else(""), "")
        self.assertEqual(none.toto().or_else("titi"), "titi")
        self.assertEqual(option("TOTO").capitalizes().or_else("t"), "t")
        self.assertEqual(option("toto").capitalize().or_else("failed"), "Toto")
        self.assertEqual(option("riri").count("ri").get(), 2)
        self.assertEqual(option(A(5)).x.get(), 5)
        self.assertEqual(option(A(5)).z.or_else(0), 0)
        option("value")()

    def test_nested_option(self):
        nested_none = option(option(option("tata")))
        for n in nested_none:
            self.assertEqual(n, "tata")

    def test_if_false(self):
        op = opt("value").or_else("")
        self.assertEqual(len(op), 5)
        print(option("value").get_or("") is none)

        self.assertEqual(opt("value").or_none(), "value")
        self.assertEqual(opt("value").or_raise(ValueError()), "value")
        self.assertEqual(option([]).or_if_falsy([1, 2, 3]), [1, 2, 3])

    def test_flat_map(self):
        nested_none = option(option(option("tata"))).map(lambda v: v + "titi").get()
        self.assertEqual(nested_none, "tatatiti")

    def test_match(self):

        value = opt_from_call(lambda: 1).get()
        self.assertEqual(value, 1)

        self.assertEqual(opt_from_call(lambda: 1 / 0).or_else(1), 1)

        match opt("tata"):
            case Some():
                print("Is Some")
            case Err(e):
                raise e
            case Empty():
                print("Empty")

        match opt(None):
            case Some(x):
                print(x)
            case Err(e):
                raise e
            case Empty():
                logger.debug("Empty")

        match Err(HttpException(400, detail="toto")):
            case Err(HttpException(code=x)):
                print(f"Got {x} code from error")

        value = opt("tata").match(
            when(Some("tata")).then(lambda: "match first"),
            when(Some(__)).then(lambda x: x * 2),
            default() >> (partial(raise_error, MatchError())),
        )

        logger.debug("value: " + value)

        value = opt("tata").match(
            when(Some("tati")).then(lambda: "match first"),
            when(Some(__)).then(lambda x: x * 2),
            default() >> (partial(raise_error, MatchError())),
        )

        logger.debug("value: " + value)

        with self.assertRaises(MatchError):
            value = opt("tata").match(
                when(Some("tati")).then(lambda: "match first"),
                when(Some("tita")).then(lambda x: x * 2),
                default() >> (partial(raise_error, MatchError())),
            )
            logger.debug("value: " + value)

        value = opt("tata").match(
            when(Some("tati")).then(lambda: "match first"),
            when(Some("tita")).then(lambda x: x * 2),
            default() >> (lambda: 1),
        )

        value = opt({1: 5, 2: {3: 12}}).match(
            Some({__: __, 2: __}) >> (lambda x, y, z: (x, y, z)),
            default() >> (lambda: None),
        )

        self.assertEqual(none.or_if_falsy(lambda x: x + 1, 1), 2)

        with self.assertRaises(EmptyError):
            none.or_raise(EmptyError())

        err(EmptyError()).unwrap()

        logger.debug(option(EmptyError()))

        self.assertIs(none.or_none(), None)

        with self.assertRaises(MatchError):
            none.match(Some(_) >> identity)

        logger.debug(when(1))

        with self.assertRaises(ZeroDivisionError):
            opt_from_call(lambda: 1 / 0, exc=ZeroDivisionError).or_raise()

        with self.assertRaises(ValueError):
            opt_from_call(lambda: 1 / 0, exc=ZeroDivisionError).or_raise(
                ValueError("An error occurred")
            )

        with self.assertRaises(ValueError):
            none.or_raise()

    def test_func(self):
        f = raise_err(ValueError("An error occurred"))
        with self.assertRaises(ValueError):
            f()
