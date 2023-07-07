![seito](img/seito.png)

# Introduction

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

## Result monad

The Result Monad is another concept from functional programming that is used to handle computations that may produce a successful result or a failure. It provides a way to encapsulate the outcome of an operation, allowing you to handle and propagate errors in a controlled manner.

The Result Monad typically has two possible states: Ok (representing a successful result) and Err (representing a failure or an error condition). The Ok state contains the successful result value, while the Err state contains information about the failure, such as an error message or an error object.

The Result Monad offers several benefits:

- Explicit error handling: It makes error handling explicit and separates the handling of successful results from error conditions.
- Propagation of errors: It allows errors to be easily propagated through a chain of operations, avoiding the need for explicit error-checking at each step.
- Composition: It enables the chaining and composition of operations on results in a concise and expressive manner.
- Error recovery: It provides mechanisms to handle and recover from errors, such as by mapping to alternative values or applying fallback strategies.

# Getting started

Simply install `seito` coming directly from pypi with your favorite python package manager.
This will install all needed dependencies.

!!! note "made with pdm"
    seito uses **pdm** as dependency manager

## with package manager

=== "poetry"
    ```bash
    poetry add seito
    ```

=== "pdm"
    ```bash
    pdm add seito
    ```

=== "pip"
    ```bash
    pip install seito
    ```

## Note on type checking

*Seito* has been developed in VSCode using Pyright type checker (with Pylance).
A focus has been made on type checking and providing decent completion with this setup.

A first run on mypy showed a lot of error not picked up by pyright, the idea is to fix
those errors as soon as possible to be mypy compliant.


🥇 that's it, ready to save some code...

