from descriptor_tools.unboundattr import UnboundAttribute
from functools import wraps


class GetDescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, instance, owner):
        result = self.desc.__get__(instance, owner)
        if result is self.desc:
            return self
        elif isinstance(result, UnboundAttribute):
            result.descriptor = self
        return result


class SetDescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __set__(self, instance, value):
        self.desc.__set__(instance, value)


def binding(get):
    @wraps(get)
    def __get__(desc, instance, owner):
        if instance is None:
            return UnboundAttribute(desc)
        else:
            return get(desc, instance, owner)
    return __get__


class Binding(GetDescriptorDecorator):
    pass  # TODO - the decorator kind