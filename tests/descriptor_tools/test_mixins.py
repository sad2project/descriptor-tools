from unittest import TestCase

from descriptor_tools import UnboundAttribute, DescDict
from descriptor_tools.mixins import (BindingDataDescriptor,
                                     NonBindingDataDescriptor,
                                     BindingGetter)
from tests.descriptor_tools import test_mocks as mocks


class BindingDataDescriptorMixin_Test(TestCase):
    class Desc(BindingDataDescriptor):
        pass

    def setUp(self):
        self.desc = self.Desc()
        self.instance = mocks.ClassWithDescriptor(self.desc)
        self.Class = type(self.instance)

    def test_get_from_instance(self):
        self.desc.storage[self.instance] = 5

        result = self.desc.__get__(self.instance, self.Class)

        self.assertEqual(result, 5)

    def test_get_from_class_is_UnboundAttribute(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIsInstance(result, UnboundAttribute)

    def test_get_from_class_has_correct_descriptor(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIs(result.descriptor, self.desc)

    def test_get_from_class_has_correct_owner(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIs(result.owner, self.Class)

    def test_set(self):
        self.desc.__set__(self.instance, 5)

        self.assertEqual(self.desc.storage[self.instance], 5)

    def test_delete(self):
        self.desc.storage[self.instance] = 5

        self.desc.__delete__(self.instance)

        self.assertNotIn(self.instance, self.desc.storage)

    def test_get_from_instance_as_property(self):
        self.desc.storage[self.instance] = 5

        result = self.instance.attr

        self.assertEqual(result, 5)

    def test_get_from_class_as_property_is_UnboundAttribute(self):
        result = self.Class.attr

        self.assertIsInstance(result, UnboundAttribute)

    def test_get_from_class_as_property_has_correct_descriptor(self):
        result = self.Class.attr


        self.assertIs(result.descriptor, self.desc)

    def test_get_from_class_as_property_has_correct_owner(self):
        result = self.Class.attr

        self.assertIs(result.owner, self.Class)

    def test_set_as_property(self):
        self.instance.attr = 5

        self.assertEqual(self.desc.storage[self.instance], 5)

    def test_delete_as_property(self):
        self.desc.storage[self.instance] = 5

        del self.instance.attr

        self.assertFalse(self.instance in self.desc.storage)


class NonBindingDataDescriptorMixin_Test(TestCase):
    class Desc(NonBindingDataDescriptor):
        pass

    def setUp(self):
        self.desc = self.Desc()
        self.instance = mocks.ClassWithDescriptor(self.desc)
        self.Class = type(self.instance)

    def test_get_from_instance(self):
        self.desc.storage[self.instance] = 5

        result = self.desc.__get__(self.instance, self.Class)

        self.assertEqual(result, 5)

    def test_get_from_class(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIs(result, self.desc)

    def test_set(self):
        self.desc.__set__(self.instance, 5)

        self.assertEqual(self.desc.storage[self.instance], 5)

    def test_delete(self):
        self.desc.storage[self.instance] = 5

        self.desc.__delete__(self.instance)

        self.assertNotIn(self.instance, self.desc.storage)

    def test_get_from_instance_as_property(self):
        self.desc.storage[self.instance] = 5

        result = self.instance.attr

        self.assertEqual(result, 5)

    def test_get_from_class(self):
        result = self.Class.attr


        self.assertIs(result, self.desc)

    def test_set_as_property(self):
        self.instance.attr = 5

        self.assertEqual(self.desc.storage[self.instance], 5)

    def test_delete_as_property(self):
        self.desc.storage[self.instance] = 5

        del self.instance.attr

        self.assertFalse(self.instance in self.desc.storage)


class BindingGetter_Test(TestCase):
    class Desc(BindingGetter):
        def __init__(self):
            self.storage = DescDict()

        def _get(self, instance):
            return self.storage[instance]

    def setUp(self):
        self.desc = self.Desc()
        self.instance = mocks.ClassWithDescriptor(self.desc)
        self.Class = type(self.instance)

    def test_get_from_class_is_UnboundAttribute(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIsInstance(result, UnboundAttribute)

    def test_get_from_class_has_correct_descriptor(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIs(result.descriptor, self.desc)

    def test_get_from_class_has_correct_owner(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIs(result.owner, self.Class)

    def test_get_from_instance(self):
        self.desc.storage[self.instance] = 5
        result = self.desc.__get__(self.instance, self.Class)

        self.assertEqual(result, 5)











































































