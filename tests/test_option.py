import logging
import typing
import unittest
from functools import partial

import pytest
from assertpy import assert_that

from seito.http import HttpException
from seito.monad.container import EmptyError
from seito.monad.func import (
    MatchError,
    _,
    default,
    identity,
    raise_err,
    raise_error,
    when,
)
from seito.monad.option import Empty, Null, Some, lift_opt, none, opt, option
from seito.monad.result import Err, Ok


class A:
    def __init__(self, x):
        self.x = x


class Test(unittest.TestCase):
    def test_option_none_get(self):
        with self.assertRaises(EmptyError):
            none.get()

    def test_option_is_empty(self):
        self.assertTrue(none.is_empty())
        value = "hello world"
        self.assertFalse(option(value).is_empty())

    def test_option_or_else(self):
        value = 1
        self.assertEqual(none.or_(value), 1)
        self.assertEqual(none.or_else(lambda: 1), 1)
        self.assertEqual(option(value).map(lambda v: v + 1).or_else(0), 2)

    def test_option_map(self):
        none_value = None
        one_value = 1
        with self.assertRaises(ValueError):
            option(none_value).map(lambda v: v + 1).get()
        self.assertEqual(option(none_value).map(lambda v: v + 1).or_(2), 2)
        self.assertEqual(option(one_value).map(lambda v: v + 1).get(), 2)

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
        # option("value")()

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
        self.assertEqual(option([]).or_if_falsy(lambda: [1, 2, 3]), [1, 2, 3])

    def test_flat_map(self):
        nested_none = (
            option(option(option("tata"))).flatten().map(lambda v: v + "titi").get()
        )
        xxxx: Some[int] = Some(1)
        xxxx.flatten()
        q = Some(Some(1))
        qq = q.flatten()
        r = Some(Some(Some(Some(1))))
        r.flatten()
        v = option(option(option("tata")))
        v.flatten()
        option(option(None))

        xx: Some[Some[Empty]] = Some(Some(Null))
        xx.flatten()

        v.flatten()
        z = Some(Some(1))
        z.flatten().map(lambda v: v + 1).get()

        qq = Some(1)
        qq.flatten()

        tt = Empty()
        tt.flat_map()
        self.assertEqual(nested_none, "tatatiti")

    def test_match(self):
        value = lift_opt(lambda: 1)().get()
        self.assertEqual(value, 1)

        with self.assertRaises(ZeroDivisionError):
            lift_opt(lambda: 1 / 0)().or_(1)

        match opt("tata"):  # noqa: E999
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
                logging.debug("Empty")

        match Err(HttpException(400, detail="toto")):
            case Err(HttpException(code=x)):
                print(f"Got {x} code from error")

        value = opt("tata")
        x = when(Some(_)).then(lambda x: "match first")
        default >> (partial(raise_error, MatchError()))
        value.match(
            when(Some(_)).then(lambda x: "match first"),
            when(Some(_)).then(lambda x: x * 2),
            default >> (partial(raise_error, MatchError())),
        )

        logging.debug("value: {} ", value)

        t = opt("tata")

        match t:
            case Some("tati"):
                value = "match first"
            case Some(val):
                value = val * 2

        logging.debug("value: " + value)

        with self.assertRaises(MatchError):
            match opt("tata"):
                case Some("tati"):
                    value = ("match first",)
                case Some("tita" as p1):
                    value = p1 * 2
                case _:
                    raise MatchError()

        match opt("tata"):
            case Some("tati"):
                value = "match first"
            case Some("tita" as p1):
                value = (p1 * 2,)
            case _:
                value = 1

        assert_that(value).is_equal_to(1)

        match opt({1: 5, 2: {3: 12}}):
            case Some({1: val1, 2: val2}):
                value = val1, val2
            case _:
                value = None
        assert_that(value).is_equal_to((5, {3: 12}))

        self.assertEqual(none.or_if_falsy(lambda x: x + 1, 1), 2)

        with self.assertRaises(EmptyError):
            none.or_raise(EmptyError())

        # err(EmptyError()).get()

        logging.debug(option(EmptyError()))

        self.assertIs(none.or_none(), None)

        with self.assertRaises(MatchError):
            none.match(Some(_) >> identity)  # type: ignore

        with self.assertRaises(ZeroDivisionError):
            lift_opt(lambda: 1 / 0)().or_raise()

        with self.assertRaises(ZeroDivisionError):
            lift_opt(lambda: 1 / 0)().or_raise(ValueError("An error occurred"))

        with self.assertRaises(ValueError):
            none.or_raise()

    def test_func(self):
        f = raise_err(ValueError("An error occurred"))
        with self.assertRaises(ValueError):
            f()

    def test_func_lift(self):
        def divide(a: int, b: int) -> float:
            return a / b

        lifted = lift_opt(divide)
        with pytest.raises(ZeroDivisionError):
            val = lifted(1, 0).or_else(1)

        val = lifted(0, 1).or_else(0)
        self.assertEqual(val, 0)

    def test_pampy_match(self):
        val = opt({1: 5, 2: {3: 12}})
        m1, m2 = val.match(*(Some({1: _, 2: _}), default >> (1, 2)))
        assert_that(m1).is_equal_to(5)
        assert_that(m2).is_equal_to({3: 12})

        default >> "No value"

        v = opt(dict(access_token="toto")).match(
            *(Some({"access_token": _}), (default >> "No value"))
        )
        val = opt(ValueError).match(Some(typing.Type[ValueError]))
        logging.debug(val)

        assert_that(Some(1).is_some()).is_true()
        assert_that(none.is_some()).is_false()

        v = opt(1)
        val = Some(1) >> identity
        v.match(*(Some(_), default >> 2))
        val = opt(1).match(Some(2) >> identity, default >> (lambda: 100))
        assert_that(val).is_equal_to(100)

        v = Ok(_) >> identity
        with pytest.raises(MatchError):
            cc = opt(1)
            cc.match(Ok(_) >> identity)

        Some(Some(1))

        # hh = vvv.match(Some(Some(_)) >> identity, default >> 10)
        # assert_that(hh).is_equal_to(1)

        opt(1).match(Some(_) >> (lambda x: str(x)))

        opt(1).match(
            *(Some(_under=2) >> (lambda x: str(x)), (default >> (lambda: 100)))
        )

        opt(1).match(*(Some(2) >> (lambda x: str(x)), default >> (lambda: "100")))

        opt(1).match(*(Some(_), default >> 100))
        opt(1).match(Some(_))
