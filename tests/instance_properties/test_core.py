# coding=utf-8
from unittest import TestCase

from descriptor_tools.instance_properties import (
                                        InstanceProperty)


class MockDelegatedProperty:
    def __init__(self, value):
        self.value = value
        self.get_called = False
        self.set_called = False

    def set_meta(self, *args):
        pass

    def get(self):
        self.get_called = True
        return self.value

    def set(self, value):
        self.set_called = True
        self.value = value


class InstancePropertyTest(TestCase):
    class Class:
        attr = InstanceProperty()

    def test_when_uninitialized_instance_when_calling_get_then_fails(self):
        instance = self.Class()

        with self.assertRaises(AttributeError):
            _ = instance.attr

    def test_given_initialized_instance_when_calling_get_then_gets_value(self):
        instance = self.Class()
        instance.attr = MockDelegatedProperty(5)

        result = instance.attr

        self.assertEqual(5, result)

    def test_given_initialized_instance_when_calling_get_then_gets_value_from_delegated_property(self):
        instance = self.Class()
        instance.attr = MockDelegatedProperty(5)

        _ = instance.attr
        delegprop = instance._attr

        self.assertTrue(delegprop.get_called)

    def test_given_uninitialized_instance_when_setting_a_non_delegate_then_raise_exception(self):
        instance = self.Class()

        with self.assertRaises(AttributeError):
            instance.attr = 5

    def test_given_initialized_instance_when_calling__set__then_set_on_delegate(self):
        instance = self.Class()
        instance.attr = MockDelegatedProperty(1)

        instance.attr = 5

        self.assertTrue(
                instance._attr.set_called,
                "set not called on delegated property")

    def test_given_initialized_instance_when_calling__set__then_set_value(self):
        instance = self.Class()
        instance.attr = MockDelegatedProperty(1)

        instance.attr = 5

        self.assertEqual(5, instance.attr)

    def test_given_nondeletable_instance_property_when_delete_then_raise_error(self):
        instance = self.Class()
        instance.attr = MockDelegatedProperty(5)

        with self.assertRaises(AttributeError):
            del instance.attr

    def test_given_initialized_readonly_delegate_when_calling__set__then_raise_exception(self):
        class ReadOnlyAttrClass:
            attr = InstanceProperty(readonly=True)

            def __init__(self):
                self.attr = MockDelegatedProperty(5)

        instance = ReadOnlyAttrClass()

        with self.assertRaises(AttributeError):
            instance.attr = 1
