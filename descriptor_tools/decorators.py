from . import UnboundAttribute, name_of
from functools import wraps


# ******************************************************
# Instance decorators (old-fashioned Design Pattern Way)
# ******************************************************
class DescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, instance, owner):
        if not is_data_desc(self.desc):  # attempt instance lookup before using
            try:                         # descriptor if non-data descriptor
                return instance.__dict__[name_of(self, owner)]
            except KeyError:
                pass

        if hasattr(self.desc, '__get__'):  # delegate if __get__ exists
            return lifted_desc_results(self.desc, self, instance, owner)
        else:  # last ditch effort: self is all that's left under that name
            return self

    def __set__(self, instance, value):
        if is_data_desc(self.desc):
            if hasattr(self.desc, '__set__'):  # delegate if __set__ exists
                self.desc.__set__(instance, value)
            else:  # bad call if it's a data descriptor without __set__
                raise AttributeError('__set__')
        else:  # delegate to instance dictionary
            name = name_of(self, type(instance))
            instance.__dict__[name] = value

    def __delete__(self, instance):
        if is_data_desc(self.desc):
            if hasattr(self.desc, '__delete__'):  # delegate if __delete__ exists
                self.desc.__delete__(instance)
            else:  # bad call if it's a data descriptor without __delete__
                raise AttributeError('__delete__')
        else:  # delegate to instance dictionary
            name = name_of(self, type(instance))
            del instance.__dict__[name]

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