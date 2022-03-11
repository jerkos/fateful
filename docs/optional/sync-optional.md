# Sync Optional

Seito exposes a famous container for dealing with `None` or more generally speaking
empty values (i.e. in python all instances of collections which are falsy).

It is called `Optional`. Basically, two classes derives from this base class, `Some`
which represents a computed result which is not None or not falsy, and at the opposite
`Empty` which is a wrapper of None or falsy values.

!!! note "mypy compliant target"
    all the methods are typed to allow decent code completion

## Examples

Let's take a look at the code and api to get the basis:

```py linenums="1"
from seito import opt

# optional is Some[str]
opt('value').or_else('new value')

# optional are mappable, returns VALUE
opt('value').map(str.upper).or_else("UNKNOWN")
none.map(str.upper).or_else("UNKOWN") # returns UNKNOWN

# will raise an error
opt(None).get() # same as none.get()

# optional are iterable
a = opt('optional option value')
for i in a: 
    print(i)
```

## Forwarding value
One funny things is that you can forward a computation, like this

```py linenums="1"
from seito import opt
# forwarding value
class A:
    x = 5
        
opt(A()).x.or_else(0) # returns 5
opt(A()).y.or_else(0) # returns 0
```

## Pattern matching on options
We also can use pattern matching:

```python linenums="1"
from seito import opt, Some, Empty, default

result = opt("value").match(
    Some(_) >> 1,
    default() >> 0
)
```

## Real cases
In a real case example, it leads to this:

```py linenums="1"

def translate(value: str) -> str | None:
    if not value:
        return "world"
    if value == 'hello':
        return ', world'
    elif value == 'world':
        return ""
    return None

value = translate("Marco")
opt(value).map(
```





## Api

**get(self) -> Any**

**is_empty(self) -> bool**

**or_else(self, obj: Callable[..., Any] | Any, \*args: Any, \*\*kwargs: Any) -> Any**

**or_if_falsy(self, obj: Callable[..., Any] | Any, \*args: Any, \*\*kwargs: Any) -> Any**

**or_none(self) -> Any**

**or_raise(self, exc: Exception)**

**map(self, func: Callable[..., Any], \*args: Any, \*\*kwargs: Any) -> "Option"**

**__iter__(self)**

**__getattr__(self, name: str) -> Any**

**__call__(self, \*args: Any, \*\*kwargs: Any)**

**__str__(self) -> str**

**__rshift__(self, other) -> When**

**match(self, \*whens: When | Default)**