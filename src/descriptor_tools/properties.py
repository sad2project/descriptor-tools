# coding=utf-8
from descriptor_tools import name_of

from descriptor_tools.decorators import binding

__author__ = 'Jake'
__all__ = ['LazyProperty', 'BindingProperty', 'withConstants']


class LazyProperty:
    """
    A `Lazy Property` is a property that is defined early on, but is not
    evaluated until later. To do this, it is provided with a function that
    will be executed the first time the property is accessed. The result
    of that function will then be stored as the result from then on.
    
    The easiest way to use `Lazy Property` is as a decorator for a method.
    A good example is for a `Circle` class:
    
        class Circle:
            def __init__(self, radius):
                self.radius = radius
                
            @LazyProperty
            def diameter(self):
                return self.radius * 2
                
            @LazyProperty
            def circumference(self):
                return 2 * 3.14 * self.radius
                
            @LazyProperty
            def area(self):
                return 3.14 * pow(self.radius, 2)
    
    The attributes of a circle can be calculated just from the radius, but
    there's no reason to calculate and store those values until/unless you 
    need them. `LazyProperty` allows those values to remain uncalculated
    until then.
    
    Note: If you use a lambda as the function from which to calculate the
    lazy value, you must provide `named=False` as an argument to the
    `LazyProperty` constructor.
    """
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
        if instance is None:
            return "<unknown name>"
        name = name_of(self, type(instance))
        self._name = lambda inst: name
        return name

    def __str__(self):
        """
        Returns a string representation of the the instance.
        
        If `named=False` was given in the constructor, this method
        will say the name of the property is `"<unknown name>"` until
        `__get__()` is called with an instance at least once.
        """
        return "Lazy Property: " + self._name(None)

    def __repr__(self):
        """
        Returns a debugger string representation of the the instance.
        
        If `named=False` was given in the constructor, this method
        will say the name of the property is `"<unknown name>"` until
        `__get__()` is called with an instance at least once.
        """
        return self.__str__() +" "+ id(self)


class BindingProperty(property):
    """
    `BindingProperty` is exactly like `property` except that it 
    provides bound attributes.
    """
    def __call__(self, instance):
        return self.__get__(instance)


class Constant:
    """
    `Constant` is used for exactly what the name implies. The
    intended way to use it is to define a `Constant` on a
    metaclass, which a class will then inherit from. This allows
    you to access the constant with `ClassName.CONSTANT_NAME`
    without worry of it being changed. 
    
    Technically, it still can be changed, but that requires
    monkey-patching a metaclass.
    
    The constant cannot be accessed from an instance of the class
    (i.e. `instance_name.CONSTANT_NAME`) like many class attributes.
    
    For a simple way of creating the needed metaclasses, see the
    function, `withConstants()`
    """
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        raise AttributeError("Cannot alter a constant")

    def __delete__(self, instance):
        raise AttributeError("Cannot delete a constant")

    def __str__(self):
        return "CONSTANT:" + str(self.value)


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







