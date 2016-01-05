from descriptor_tools.unboundattr import UnboundAttribute
from functools import wraps


# ******************************************************
# Instance decorators (old-fashioned Design Pattern Way)
# ******************************************************
class GetDescDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, instance, owner):
        result = self.desc.__get__(instance, owner)
        if result is self.desc:
            return self
        elif isinstance(result, UnboundAttribute):
            return result.lift_descriptor(self)
        return result

    def __getattr__(self, item):
        return getattr(self.desc, item)


class SetDescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __set__(self, instance, value):
        self.desc.__set__(instance, value)


class Binding(GetDescDecorator):
    pass  # TODO - the decorator kind


class SecretSet(SetDescriptorDecorator):
    pass


class ForcedSet(SetDescriptorDecorator):
    pass


class SetOnce(SetDescriptorDecorator):
    pass


# *****************
# Method decorators
# *****************
def binding(get):
    @wraps(get)
    def __get__(desc, instance, owner):
        if instance is None:
            return UnboundAttribute(desc)
        else:
            return get(desc, instance, owner)
    return __get__