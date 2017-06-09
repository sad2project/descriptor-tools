# coding=utf-8
"""
# descriptor-tools
A collection of classes and functions to make the creation of descriptors
simpler and quicker. Most of the ideas present in this library were presented,
but not fully fleshed out in my book (link to the book), *Python Descriptors: A
Comprehensive Guide*.

The first major contribution that this library provides is attribute binding
(see below), along with many helpers for building descriptors that use it.

The next major contribution is a set of decorators (GoF style AND method
decorators) and mixins, both of which are the only modules that cannot have its
members accessed directly from the descriptor_tools package. While everything
else that's public is available from there, the decorators have to be accessed
from descriptor_tools.decorators, and the mixins have to be accessed from
`descriptor_tools.mixins`.

See the documentation of the corresponding modules to read more about them.

### Attribute Binding
Attribute binding is just like method binding in Python. When you refer to a
method through its class name without calling it (e.g. `ClassName.method_name`),
you get a version of the method that can accept an instance (and whatever other
necessary arguments) when it is called, rather than being bound directly to the
instance. These were once called "unbound methods" in Python 2, but now they're
just implemented as functions in Python 3.

Nevertheless, they are still unbound methods. And now it's possible to have
unbound attributes. If an attribute is defined using a descriptor that uses
attribute binding, you can get an unbound attribute from a class
(e.g. `ClassName.attr_name`), which can then be called like a function which
takes an instance as a parameter and returns the attribute value for that
instance. Check out the documentation on `UnboundAttribute` for benefits of this
technique.

### Special Accessor Types
In the book, there were four different special ways of accessing, and these
ideas are spread throughout this code base.

The first one is a binding descriptor, which implements attribute binding,
mentioned above.

The other three are different ways of implementing "read-only" attributes:
set-once, forced-set, and secret-set.

The set-once type only allows for `__set__()` to be called once per instance. If
it's ever tried again, it raises an `AttributeError`.

The forced-set method is similar to the secret-set method in that they both
allow the attribute to be set multiple times, but it must be done in a
roundabout way through a back door. Forced-set allows you call the usual
`__set__()` method  on the descriptor, but it must be provided with the named
argument, `force=True` in order for it to not raise an `AttributeError`.

Secret-set descriptors use a "secret" method to set the attribute, which is
usually the `set()` method (as opposed to the `__set__()` method). This is g
enerally preferred over the forced-set style because it doesn't require someone
to explicitly call a "magic" method, and it doesn't alter the signature of a
protocol method.

### Other Points of Note
There are quite a few little helper functions and classes within the library,
most notably those for grabbing descriptor objects from classes (preventing the
lookup from triggering the descriptor's `__get__()` method) and those for
providing universal ways to assign values to attributes when they're read-only
(since a back door must usually be present for initializing the value).

Lastly, there are a few new "property" types: `BindingProperty`, which provides
attribute binding to properties; constants, defined using the `withConstants()`
function; and `LazyProperty`, which allows lazy instantiation of properties,
given a evalutation method.
"""
from descriptor_tools.desc_dict import DescDict
from descriptor_tools.find_descriptors import (get_descriptor_from,
                                               get_descriptor)
from descriptor_tools.names import (name_of,
                                    id_name_of)
from descriptor_tools.set_attrs import (AttributeSetter,
                                        mangle_name,
                                        NameMangler,
                                        set_on,
                                        setattribute,
                                        Setter)
from descriptor_tools.unboundattr import UnboundAttribute
from descriptor_tools.properties import (BindingProperty,
                                         LazyProperty,
                                         withConstants)

# does not automatically export the decorators or mixins modules

__all__ = ['AttributeSetter',
           'BindingProperty',
           'DescDict',
           'get_descriptor',
           'get_descriptor_from',
           'LazyProperty'
           'mangle_name',
           'NameMangler',
           'name_of',
           'id_name_of',
           'set_on',
           'setattribute',
           'Setter',
           'UnboundAttribute',
           'withConstants',
           'Binding',
           'binding',
           'forced',
           'ForcedSet',
           'SecretSet',
           'set_once',
           'SetOnce',
           'is_data_desc',
           'DescriptorDecoratorBase']
