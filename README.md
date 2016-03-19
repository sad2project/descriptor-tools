[![Python](https://img.shields.io/badge/Python-3.x-brightgreen.svg)](https://www.python.org/)
[![1st edition](https://img.shields.io/badge/Edition-1.0-AA3333.svg)](link to my book on amazon)
# descriptor-tools
A collection of classes and functions to make the creation of descriptors simpler and quicker. Most of the ideas present in this library were presented, but not fully fleshed out in my book (link to the book), *Python Descriptors: A Comprehensive Guide*.

The first major contribution that this library provides is attribute binding (see below), along with many helpers for building descriptors that use it.

The next major contribution is a set of decorators (GoF style AND method decorators) and mixins, both of which are the only modules that cannot have its members accessed directly from the descriptor_tools package. While everything else that's public is available from there, the decorators have to be accessed from descriptor_tools.decorators, and the mixins have to be accessed from descriptor_tools.mixins.

See the documentation of the corresponding modules to read more about them.

### Attribute Binding
Attribute binding is just like method binding in Python. When you refer to a method through its class name without calling it (e.g. `ClassName.method_name`), you get a version of the method that can accept an instance (and whatever other necessary arguments) when it is called, rather than being bound directly to the instance. These were once called "unbound methods" in Python 2, but now they're just implemented as functions in Python 3. 

Nevertheless, they are still unbound methods. And now it's possible to have unbound attributes. If an attribute is defined using a descriptor that uses attribute binding, you can get an unbound attribute from a class (e.g. `ClassName.attr_name`), which can then be called like a function which takes an instance as a parameter and returns the attribute value for that instance. Check out the documentation on `UnboundAttribute` for benefits of this technique.

### Other Points of Note
There are quite a few little helper functions and classes within the library, most notably those for grabbing descriptor objects from classes (preventing the lookup from triggering the descriptor's `__get__()` method) and those for providing universal ways to assign values to attributes when they're read-only (since a back door must usually be present for initializing the value).

Lastly, there are a few new "property" types: `BindingProperty`, which provides attribute binding to properties; constants, defined using the `withConstants()` function; and `LazyProperty`, which allows lazy instantiation of properties, given a evalutation method.
