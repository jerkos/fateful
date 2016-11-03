# seito
functional python (for learning)

Python has some great functional features. The most notable ones are
comprehensions. However, when you start to chain function calls (or predicate
 or whatever), it becomes rapidly a pain to me.
 
After using Java8 and those fucking greats lambdas during almost one year, 
I just wanted to implement that kind of syntactic sugar for Python the simplest way.

There are 3 main modules:
* option module: simplest implementation of the option monad 
([See option in Scala](http://www.scala-lang.org/api/2.11.8/index.html#scala.Option))
``` python
from seito import opt, none
>>> opt('value').or_else('new value')
value
>>> opt(None).get() # same as none.get()
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
        def get_x(self):
            return self.x
        
>>> opt(A(1)).get_x().or_else(0)
1
>>> opt(A(1)).get_y().or_else(0)
0
```
* module dealing with json
``` python
>>> from seito.john import obj
>>> i = obj({'z-index': 1000})
>>> i.toto = [4, 5, 6]
>>> i.stringify()
'{"z-index": 1000, "toto": [4, 5, 6]}'
```
* sequence module
``` python
>>> from seito import seq, underscore as _
>>> seq(1, 2, 3).stream().for_each(print)
1
2
3
>>> seq(A(1), A(2), A(3)).stream().map(_.get_x()).to_list()
[1, 2, 3]

```

Notes: I found some python packages doing almost the same things. I did 
this essentially to learn and wanted to keep it simple.
