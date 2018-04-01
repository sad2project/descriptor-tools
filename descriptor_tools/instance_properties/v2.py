from descriptor_tools import name_of, DescDict
from descriptor_tools.decorators import binding


# Potential replacement for the current Instance Property system that will be even easier to use
# unfinished and untested. Do not use.


class InstanceProperty:
    def __init__(self, deleg_prop_creator):
        self._deleg_prop_creator = deleg_prop_creator
        self._prop_storage = DescDict()
        self._names = {}
        
    def __set_name__(self, owner, name):
        self._names[owner] = name
       
    def _name_for(self, owner):
        try:
            return self._names[owner]
        except KeyError:
            self._names[owner] = name_of(self, owner)
            return self._names[owner]
    
    @binding
    def __get__(self, instance, owner):
        try:
            return self._prop_storage[instance].get()
        except KeyError:
            raise AttributeError("Attribute not initialized")  # TODO: word error the same as for a normal attribute error
    
    
    def __set__(self, instance, value):
        try:
            property = self._prop_storage[instance]
        except KeyError:
            property = self._deleg_prop_creator(value, self._name_for(type(instance)), instance)
            self._prop_storage[instance] = property
        property.set(value)
        
    def __delete__(self, instance):
        try:
            property = self._prop_storage[instance]
        except KeyError:
            raise Exception()  # TODO: raise an error similar to the one you'd get if you tried to delete a non-existant instance attribute
        if hasattr(property, "do_not_delete") and not property.do_not_delete:  # in order to NOT delete it, we need the delegated property to have the do_not_delete attribute and have it set to True/truthy
            try:
                property.delete()  # delegated properties can implement a delete() to do any necessary cleanup
            except AttributeError:
                pass
            del self._prop_storage[instance]
        else:
            raise Exception()  # TODO: raise some sort of error that says that the attribute cannot be deleted