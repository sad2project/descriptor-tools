"""
The `mixins` module provides, as its name implies, a set of mix-ins that can
be used to create new descriptors with certain properties. Potentially, one
could create entire descriptors just with mix-ins, though they'd just be
glorified attributes with no unique functionality.

They're all namespaced into groups according to method the partially implement
for you or the way that the values for the attributes are stored. These 
namespaces are `Getters`, `Setters`, and `Storage`.

Each mix-in implements a *part* of a method's functionality, then delegates the
rest to a different method for you to implement. Interestingly, the `Storage`
mixins actually implement the delegated-to methods that the other 2 types (3,
if there were any `Deleters` mix-ins) call to finish. 

See each namespace for more about how they're implemented and how to implement
them.
"""

from descriptor_tools import DescDict, NameMangler, name_of, \
    id_name_of


__author__ = 'Jake'


class Getters:
    """
    The `Getters` classes are mix-ins for descriptors that allow the creator
    to ignore having to deal with class access of __get__().

    They implement __get__() to deal with instance being None in their
    specialized way. When an instance is actually provided, they redirect to
    self._get(instance), which subclasses must implement.
    """
    class Binding:
        """
        Binding is a mix-in that implements __get__() to return an
        UnboundAttribute when instance is None. Otherwise, it redirects as
        specified in the Getters documentation.
        """
        def __call__(self, instance):
            return self.__get__(instance)

        def __get__(self, instance, owner=None):
            if instance is None:
                return self
            else:
                return self._get(instance)

    class SelfReturning:
        """
        SelfReturning is a mix-in that implements __get__() to return self
        when instance is None. Otherwise, it redirects as specified in the
        Getters documentation.
        """
        def __get__(self, instance, owner):
            if instance is None:
                return self
            else:
                return self._get(instance)


class Storage:
    """
    The `Storage` mix-ins are for descriptors, allowing the creators to ignore
    any real implementation details for how the data is stored. They provide
    implementations of `_get()`, `_set()`, and `_delete()`, as specified by the
    documentation on `Getters`, `Setters`, and `Deleters`, respectively.

    Generally, you'll write your own sub-version of the `_get()`, `_set()`,
    and/or `_delete()` methods to take care of specialized implementation
    details, then use `super()` to call the versions provided by the mix-ins.
    
    If you're not using any of the other types of mixins, you could also just
    define the `__get__()`, `__set__()`, and `__delete__()` methods as needed
    and just delegate storage calls to `_get()`, `_set()`, and `_delete()` as
    needed.
    """
    class DescDict:
        """
        `DescDict` is a mix-in that uses the descriptor_tools.DescDict as its
        storage medium.
        """
        def __init__(self, *args, **kwargs):
            try:
                super().__init__(*args, **kwargs)
            except TypeError:
                # This is expected when the mixin is not used with multiple
                # inheritance, in which case, we just ignore it.
                pass
            self.storage = DescDict()

        def _get(self, instance):
            return self.storage[instance]

        def _set(self, instance, value):
            self.storage[instance] = 5

        def _delete(self, instance):
            del self.storage[instance]

    class KeyByName:
        """
        The `KeyByName` mix-in stores the values back onto the actual instances,
        using the name used on the descriptor as the location in the instance
        dictionary to store it. Optionally, you can provide a prefix and/or a
        postfix (via named arguments) for "mangling" the name that it's stored
        under.
        """
        def __init__(self, *args, name=None, prefix='', postfix='', **kwargs):
            try:
                super().__init__(self, *args, **kwargs)
            except TypeError:
                # This is expected when the mixin is not used with multiple
                # inheritance, in which case, we just ignore it.
                pass
            if name is None:
                self.mangle = NameMangler(prefix=prefix, postfix=postfix)
            else:
                self._name = lambda inst: name

        def _get(self, instance):
            return instance.__dict__[self._name(instance)]

        def _set(self, instance, value):
            instance.__dict__[self._name(instance)] = value

        def _delete(self, instance):
            del instance.__dict__[self._name(instance)]

        def _name(self, instance):
            name = self.mangle(name_of(self, type(instance)))
            self._name = lambda inst: name
            del self.mangle
            return name

    class KeyById:
        """
        The `KeyById` mix-in stores its values back onto its corresponding
        instances, just like `KeyByName`, except it uses a very different naming
        scheme to decide where on the instance to store it.
        
        In order to figure out where to store it, the mix-in looks up its own 
        `id()`, then changes the number to hexidecimal, and finally removes the
        `"0"` from the leading `"0x"` in order to make it a valid python 
        identifier.
        
        This technique ensures that it won't cross over with any other descriptors
        that use the same techniqe, and is very unlikely to run into problems with
        other naming techniques, since most don't use numbers as the primary part
        of the number.
        
        The downside is that any persistance techniques (serialization, pickling,
        etc.) cannot just push and pull fields from the instance's dictionary, since
        these ids will change between runs and interpreter instances. If the
        persistance is personalized for the class, it can still just use the descriptors
        to get and set the values, and it'll be fine.
        """
        @property
        def _name(self):
            return id_name_of(self)

        def _get(self, instance):
            return instance.__dict__[self._name]

        def _set(self, instance, value):
            instance.__dict__[self._name] = value

        def _delete(self, instance):
            del instance.__dict__[self._name]


class Setters:
    """
    The `Setters` classes are mix-ins for descriptors that allow the creator
    to ignore having to implementing special the setter special accessors.

    They implement `__set__()` to deal with the specifics of implementing the
    techniques, they redirect to self._set(instance), which subclasses must 
    implement.
    """
    class Forced:
        """
        `Forced` is a mix-in that implements the forced-set accessor style.
        When `__set__()` is called with `force=True`, it redirects as specified
        in the `Setters` documentation.
        """
        def __set__(self, instance, value, force=False):
            if force:
                self._set(instance, value)
            else:
                raise AttributeError("Cannot set a read-only attribute")

    class Secret:
        """
        The `Secret` mix-in implements the secret-set accessor style, where
        calls to `__set__()` fail, but calls to the `set()` backdoor work.
        
        Calls to `set()` redirect as specified in the `Setters` documentation.
        """
        def __set__(self, instance, value):
            raise AttributeError("Cannot set a read-only attribute")

        def set(self, instance, value):
            self._set(instance, value)
            
    class SetOnce:
        """
        `SetOnce` is a mix-in that only allows for a value to be set once,
        providing no back doors to assign new values later on.
        
        When `__set__()` deems it okay to assign a value, it redirects as 
        specified in the `Setters` documentation.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)
            self._instances = set()
        
        def __set__(self, instance, value):
            if instance in self._instances:
                raise AttributeError("Cannot set a read-only attribute")
            else:
                self._instances.add(instance)
                self._set(instance, value)
