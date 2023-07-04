# seito

*Option* and *Result* container for python !

![seito](./docs/img/seito.png)

documentation: https://jerkos.github.io/seito/

Python has some great functional features. The most notable ones are list / dict
comprehensions. However, when you start to chain function calls (or predicate
 or whatever), it becomes rapidly a pain.

 In some famous languages, we have *Option* and *Result* monad helping user to handle
 optional values (i.e. None values) and possibly failing computation (Rust, Java, Kotlin...)

 So, this very small Python library implements those monads - Option and Result -
 providing a way to handle optional values / computation failures in a functional style.

 A focus has been made to typing (but can still be improved of course !)


## Option monad

The Option Monad, also known as the Maybe Monad, is a concept from functional programming that provides a way to handle optional values in a more controlled and expressive manner. It helps avoid null or undefined errors by encapsulating a value that may or may not be present. The key idea behind the Option Monad is to provide a container that can either hold a value (Some) or indicate the absence of a value (None).

The Option Monad offers several benefits, including:

- Safety: It helps prevent null or undefined errors that can occur when working with optional values.
- Clarity: It makes the presence or absence of a value explicit, enhancing the readability of code.
- Composability: It allows for chaining operations on optional values without explicitly checking for null or undefined values.
- Functional style: It promotes functional programming principles by encouraging pure functions and immutability.


When you do not know if a value is None or is actually a real value / object, use **opt**
to wrap it into an option

``` python
from seito import opt, Null, Some

# Null is a singleton which is basically Empty(None)
>>> opt('value').or_('new value')
value

>>> opt('value').or_else(lambda: 'another value)
value

>>> Null.or_else(lambda: 'new value')
new value

>>> opt(None).get() # same as none.get()
Traceback (most recent call last):
...
ValueError: Option is empty
```

Option monad implements tu iteration protocl

```python
>>> o = opt([1, 2, 3]).for_each(print)
[1, 2, 3]

>>> a = opt('optional option value')
>>> for i in a:
>>>     print(i)
optional option value
```

It supports also forwarding a value

```python
>>> # forwarding value
>>> class A(object):
        def __init__(self, x):
            self.x = x
        def get_x(self):
            return self.x

>>> opt(A(1)).get_x().or_(0)
1
>>> opt(A(1)).get_y().or_(0)
0
```

A option value can be transformed into another enabling chaining operation

```python
from seito.monad.option import option
result = option("some").map(lambda x: len(x) * 2).or_(0)
```

An option can contain another option type but can be flattened

```python
x = option(option(option(1))).flatten() # x is Some[int]

y: Some[Some[Some[int]]] = Some(Some(Some(1)))
x: Some[int] = Some(Some(Some(1))).flatten()
```

We can lift an function to return an *option* type using a decorator

```python
from seito.monad.option import lift_option

@lift_option
def maybe(value: int):
    if value >= 2:
        return 2
    return None

x: Some[int] = maybe(2)
x: Empty = maybe(0)
```

## Result monad

The Result Monad is another concept from functional programming that is used to handle computations that may produce a successful result or a failure. It provides a way to encapsulate the outcome of an operation, allowing you to handle and propagate errors in a controlled manner.

The Result Monad typically has two possible states: Ok (representing a successful result) and Err (representing a failure or an error condition). The Ok state contains the successful result value, while the Err state contains information about the failure, such as an error message or an error object.

The Result Monad offers several benefits:

- Explicit error handling: It makes error handling explicit and separates the handling of successful results from error conditions.
- Propagation of errors: It allows errors to be easily propagated through a chain of operations, avoiding the need for explicit error-checking at each step.
- Composition: It enables the chaining and composition of operations on results in a concise and expressive manner.
- Error recovery: It provides mechanisms to handle and recover from errors, such as by mapping to alternative values or applying fallback strategies.

```python
def may_fail(x: int) -> float:
    return 1 / x

from seito.monad.try_ import Try

result = Try.of(may_fail).on_error((ZeroDivisionError,))(1).or_(10.0)
assert result == 1.0

result = Try.of(may_fail).on_error((ZeroDivisionError,))(0).or_(10.0)
assert result == 10.0


```

## Async Result

Async result provides exactly same functionalites than regular Result monad


```python
async def divide_async(a, b):
    await asyncio.sleep(0.1)
    return a / b

value = await async_try(add_async, 1, 1).or_else(lambda: 4)
value = await async_try(add_async, 1, 1).or_(4)
divide: AsyncResult[..., float, ZeroDivisionError] = async_try(add_async, 1, 1)
divide.on_errors((ValueError,)) # mypy / pyright complains because ZeroDiisionError does not match ValueError
result: Ok[float] | Err[ZeroDivisionError] = await divide.on_errors((ZeroDivisionError,)).execute()

# transforming value
value = await divide.map(lambda r: r - 100).or_(0)

match (await divide.on_errors((ZeroDivisionError,)).execute()):
    case Ok(val):
        return val
    case Err(err):
        raise err
    case _:
        raise TypeError("Never supposed to happen")
```

## Http module

Miscellaneous functions dealing with http client functions

Wraps aihttp for perform http call and parsing results optionnaly as json

```python

```

## Json module

Miscellaneous functions dealing with json (parsing, manipulating...)

``` python
>>> from seito.json import obj
>>> i = obj({'z-index': 1000})
>>> i.toto = [4, 5, 6]
>>> str(i)
'{"z-index": 1000, "toto": [4, 5, 6]}'
```


Notes: I found some python packages doing almost the same things. I did
this essentially to learn and wanted to keep it simple.

## Licenses

MIT
