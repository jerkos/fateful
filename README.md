# seito

functional python (for learning)
https://jerkos.github.io/seito/

Python has some great functional features. The most notable ones are
comprehensions. However, when you start to chain function calls (or predicate
 or whatever), it becomes rapidly a pain.

There are 3 main modules:
* option module: simplest implementation of the option monad 
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


Notes: I found some python packages doing almost the same things. I did 
this essentially to learn and wanted to keep it simple.
