from descriptor_tools import name_of
from descriptor_tools.decorators import binding

__all__ = ['LazyProperty', 'BindingProperty', 'withConstants']


class LazyProperty:
    def __init__(self, func, *, named=True):
        self.func = func
        if named:
            name = self.func.__name__
            self._name = lambda inst: name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self._name(instance)] = value
        return value

    def _name(self, instance):
        name = name_of(self, type(instance))
        self._name = lambda inst: name
        return name


class BindingProperty(property):
    @binding
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)


class Constant:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        raise AttributeError("Cannot alter a constant")

    def __delete__(self, instance):
        raise AttributeError("Cannot delete a constant")

def withConstants(**kwargs):
  """
  Creates a metaclass that uses read-only descriptors to create class
  constants for the class who sets the returned metaclass as its metaclass.

  For example, if you want a Math class with a PI constant that cannot be
  changed, you would define the Math class like this:

      class Math(metaclass=withConstants(PI=3.14159265358979323)):
          # the rest of the class definition as normal

  :param kwargs: the names and values of the desired constants
  :return: a new metaclass with the constants set
  """
  class MetaForConstants(type):
      pass

  for k,v in kwargs.items():
      setattr(MetaForConstants, k, Constant(v))

  return MetaForConstants







