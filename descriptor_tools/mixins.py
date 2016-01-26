from descriptor_tools import DescDict, UnboundAttribute, NameMangler, name_of, \
    id_name_of


class Getters:
    """
    The Getters classes are mix-ins for descriptors that allow the creator
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
        def __get__(self, instance, owner):
            if instance is None:
                return UnboundAttribute(self, owner)
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
    The Storage mix-ins are for descriptors, allowing the creators to ignore
    any real implementation details for how the data is stored. They provide
    implementations of _get(), _set(), and _delete(), as specified by the
    documentation on Getters, Setters, and Deleters, respectively.

    Generally, you'll write your own sub-version of the _get(), _set(),
    and/or _delete() methods to take care of specialized implementation
    details, then use super() to call the versions provided by the mix-ins.
    """
    class DescDict:
        """
        DescDict is a mix-in that uses the descriptor_tools.DescDict as its
        storage medium.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.storage = DescDict()

        def _get(self, instance):
            return self.storage[instance]

        def _set(self, instance, value):
            self.storage[instance] = 5

        def _delete(self, instance):
            del self.storage[instance]

    class KeyByName:
        def __init__(self, *args, name=None, prefix='', postfix='', **kwargs):
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
    class Forced:
        def __set__(self, instance, value, force=False):
            if force:
                self._set(instance, value)
            else:
                raise AttributeError("Cannot set a read-only attribute")

    class Secret:
        def __set__(self, instance, value):
            raise AttributeError("Cannot set a read-only attribute")

        def set(self, instance, value):
            self._set(instance, value)

    class Default:
        def __set__(self, instance, value):
            self._set(instance, value)


class Deleters:
    class Default:
        def __delete__(self, instance):
            self._delete(instance)