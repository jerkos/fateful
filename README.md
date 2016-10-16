# seito
functional python (for learning)

Python has some great functional features. The most notable ones are
comprehensions. However, when you start to chain function calls (or predicate
 or whatever), it becomes rapidly a pain to me.
 
After using Java8 and those fucking greats lambdas during almost one year, 
I just wanted to implement that kind of syntactic sugar for my lovely 
python language the simplest way.

There are 3 main modules:
* option module: simplest implementation of the option monad 
([See option in Scala](http://www.scala-lang.org/api/2.11.8/index.html#scala.Option))
``` python
from seito import opt
>>> opt('value').or_else('new value')
>>> opt(None).get()
Traceback (most recent call last):
...
ValueError: Option is empty
>>> o = opt([1, 2, 3]).map(print).or_else([])
[1, 2, 3]
>>> a = opt('optional option value')
>>> for i in a: print(i)
optional option value

>>> # forwarding value
>>> class A(object):
        def __init__(self, x):
            self.x = x
        def print_x_value(self):
            print(self.x)
>>> opt(A(1)).print_x_value().or_else(0)
1
>>> opt(A(1)).print_z_value().or_else(0)
0
```
* module dealing with json
* sequence module
``` python
>>> from seito import seq, underscore as _
>>> seq(1, 2, 3).stream().for_each(print)
1
2
3

>>>
>>> seq(A(1), A(2), A(3)).stream().map(_.print_x_value()).to_list()
1
2
3
[None, None, None]

```

Notes: I found some python packages doing almost the same things. I did 
this essentially to learn and wanted to keep it simple.
