from descriptor_tools import UnboundAttribute
from descriptor_tools.decorators import (DescriptorDecorator,
                                         Binding,
                                         SecretSet,
                                         ForcedSet)


class _Getter:
    def __get__(self, instance, owner):
        self.get_called = True
        if instance is None:
            return self
        else:
            return instance


class _Setter:
    def __set__(self, instance, value):
        self.set_called = True


class _Deleter:
    def __delete__(self, instance):
        self.delete_called = True


class Stubs:
    class NonDataDescriptor:
        def __get__(self, instance, owner):
            self.get_called = True
            return self

    class FullDataDescriptor(_Getter, _Setter, _Deleter):
        pass

    class DataDescriptorWithoutDelete(_Getter, _Setter):
        pass

    class DataDescriptorWithoutSet(_Getter, _Deleter):
        pass

    class DataDescriptorWithoutGet(_Setter, _Deleter):
        pass


class Descriptor:
    def __init__(self):
        self.storage = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            try:
                return self.storage[instance]
            except KeyError:
                raise AttributeError

    def __set__(self, instance, value):
        self.storage[instance] = value

    def __delete__(self, instance):
        del self.storage[instance]


def ClassWithDescriptor(descriptor):
    class Class:
        attr = descriptor
    return Class()


attrname = 'attr'