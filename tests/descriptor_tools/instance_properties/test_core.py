# coding=utf-8
from unittest import TestCase

from descriptor_tools.instance_properties.core import (
                                        InstanceProperty,
                                        InstancePropertyInitializer)


class MockDelegatedProperty:
    def __init__(self, value, **kwargs):
        self.value = value
        self.get_called = False
        self.set_called = False

    def get(self):
        self.get_called = True
        return self.value

    def set(self, value):
        self.set_called = True
        self.value = value


class InstancePropertyTest(TestCase):
    class Class:
        attr = InstanceProperty(MockDelegatedProperty)

    def test_given_unitialized_instance_when_calling__get__then_initializer_returned(self):
        instance = self.Class()

        initializer = instance.attr

        self.assertIsInstance(initializer, InstancePropertyInitializer)

    def test_given_initialized_instance_when_calling__get__then_gets_attribute_from_delegated_property(self):
        instance = self.Class()
        init_value = 1
        instance.attr.initialize(init_value)

        instance.attr

        self.assertTrue(
                instance._attr.get_called,
                "value not taken from delegated property")

    def test_given_initialized_instance_when_calling__get__then_returns_delegate_value(self):
        instance = self.Class()
        init_value = 1
        instance.attr.initialize(init_value)

        end_value = instance.attr

        self.assertEqual(end_value, init_value)

    def test_given_uninitialized_instance_when_calling__set__then_raise_exception(self):
        instance = self.Class()

        with self.assertRaises(AttributeError):
            instance.attr = 1

    def test_given_initialized_instance_when_calling__set__then_set_on_delegate(self):
        instance = self.Class()
        instance.attr.initialize(1)

        instance.attr = 1

        self.assertTrue(
                instance._attr.set_called,
                "set not called on delegated property")

    def test_given_initialized_readonly_delegate_when_calling__set__then_raise_exception(self):
        class ReadOnlyDelegatedProperty:
            def __init__(self, *args, **kwargs): pass
            def get(self): pass

        class Class:
            attr = InstanceProperty(ReadOnlyDelegatedProperty)

        instance = Class()
        instance.attr.initialize(1)

        try:
            instance.attr = 1
            self.fail()
        except AttributeError as e:
            self.assertIn("Cannot set new value on read-only attribute, 'attr'", str(e))
