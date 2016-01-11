from descriptor_tools import UnboundAttribute, name_of
from functools import wraps


# ******************************************************
# Instance decorators (old-fashioned Design Pattern Way)
# ******************************************************
class DescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, instance, owner):
        if not is_data_desc(self.desc):
            try:
                return instance.__dict__[name_of(self, owner)]
            except KeyError:
                pass

        if hasattr(self.desc, '__get__'):
            return lifted_desc_results(self.desc, self, instance, owner)
        else:
            return instance.__dict__[name_of(self, owner)]

    def __set__(self, instance, value):
        if hasattr(self.desc, '__set__'):  # delegate if __set__ exists
            self.desc.__set__(instance, value)
        elif is_data_desc(self.desc):  # bad call if it's a data descriptor without __set__
            raise AttributeError('__set__')
        else:  # delegate to instance dictionary
            instance.__dict__[name_of(self, type(instance))] = value

    def __delete__(self, instance):
        if hasattr(self.desc, '__delete__'):
            self.desc.__delete__(instance)
        elif is_data_desc(self.desc):
            raise AttributeError('__delete__')
        else:
            del instance.__dict__[name_of(self, type(instance))]

    def __getattr__(self, item):
        return getattr(self.desc, item)


def lifted_desc_results(wrapped, wrapper, instance, owner):
    result = wrapped.__get__(instance, owner)
    if result is wrapped:
        return wrapper
    elif isinstance(result, UnboundAttribute):
        return result.lift_descriptor(wrapper)
    else:
        return result


def is_data_desc(desc):
    return hasattr(desc, '__set__') or hasattr(desc, '__delete__')


class Binding(DescriptorDecorator):
    pass


class SecretSet(DescriptorDecorator):
    pass


class ForcedSet(DescriptorDecorator):
    pass


class SetOnce(DescriptorDecorator):
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