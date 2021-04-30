from dataclasses import dataclass, field
from .option import opt, none
from .underscore import Underscore
from typing import Callable, List
@dataclass
class Try:
  f: Callable
  as_opt: bool = True
  cb: Callable = None
  errors: List[Exception] = field(default_factory=list)

  def on_error(self, *errors, cb=lambda: None):
    if not all(issubclass(e, Exception) for e in errors):
      raise ValueError('Error')
    self.cb = cb
    self.errors = errors
    return self
  
  def __call__(self, *args, **kwargs):
    errors = tuple(self.errors) or Exception
    try:
      value = self.f.apply_f(*args, **kwargs) if isinstance(self.f, Underscore) else self.f(*args, **kwargs)
      return opt(value) if self.as_opt else value
    except errors as e:
      if self.as_opt:
        return none
      if self.cb:
        return self.cb(e)

def attempt(f):
  return Try(f)

def attempt_dec(errors=(Exception,), as_opt=False):
  def _(f):
    try_ = Try(f=f, errors=errors, as_opt=as_opt)
    def __(*args, **kwargs):
      return try_(*args, **kwargs)
    return __
  return _
  
  