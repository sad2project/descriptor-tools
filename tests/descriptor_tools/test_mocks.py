class Descriptor:
    def __init__(self):
        self.storage = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.storage[instance]

    def __set__(self, instance, value):
        self.storage[instance] = value


class UnboundAttribute:
    def __init__(self, descriptor,owner):
        self.descriptor = descriptor
        self.owner = owner

    def __call__(self, instance):
        return self.descriptor.__get__(instance, self.owner)


class DescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, instance, owner):
        return self.desc.__get__(instance, owner)

    def __set__(self, instance, value):
        self.desc.__set__(instance, value)


class Binding(DescriptorDecorator):
    def __init__(self, desc):
        super().__init__(desc)

    def __get__(self, instance, owner):
        if instance is None:
            return UnboundAttribute(self, owner)
        else:
            super().__get__(instance, owner)


class ForcedSet(DescriptorDecorator):
    def __init__(self, desc):
        super().__init__(desc)

    def __set__(self, instance, value, force=False):
        if force:
            super().__set__(instance, value)
        else:
            raise AttributeError()


class SecretSet(DescriptorDecorator):
    def __init__(self, desc):
        super().__init__(desc)

    def __set__(self, instance, value):
         raise AttributeError()

    def set(self, instance, value):
         super().__set__(instance, value)


def ClassWithDescriptor(descriptor):
    class Class:
        attr = descriptor
    return Class()


class ClassWithOutDescriptor:
    pass


attrname = 'attr'