from unittest import TestCase

from descriptor_tools import UnboundAttribute
from descriptor_tools.properties import (LazyProperty,
                                         BindingProperty,
                                         withConstants)


class LazyProperty_NormalFunction_Test(TestCase):
    class Class:
        @LazyProperty
        def prop(self):
            return 5

    def setUp(self):
        self.instance = self.Class()

    def test_instance_does_not_initially_have_value(self):
        self.assertFalse('prop' in self.instance.__dict__)

    def test_correct_returned_value_from_instance(self):
        value = self.instance.prop

        self.assertEqual(value, 5)

    def test_value_is_on_instance_after_first_lookup(self):
        self.instance.prop

        self.assertTrue('prop' in self.instance.__dict__)

    def test_correct_value_on_instance_after_first_lookup(self):
        self.instance.prop

        self.assertEqual(self.instance.__dict__['prop'], 5)


class LazyProperty_MiscFunction_Test(TestCase):
    class Class:
        # use named=False to signify that it can't derive its name from
        # the function passed in
        prop = LazyProperty(lambda self: 5, named=False)

    def setUp(self):
        self.instance = self.Class()

    def test_instance_does_not_initially_have_value(self):
        self.assertFalse('prop' in self.instance.__dict__)

    def test_correct_returned_value_from_instance(self):
        value = self.instance.prop

        self.assertEqual(value, 5)

    def test_value_in_instance_after_first_lookup(self):
        self.instance.prop

        self.assertTrue('prop' in self.instance.__dict__)

    def test_correct_value_on_instance_after_first_lookup(self):
        self.instance.prop

        self.assertEqual(self.instance.__dict__['prop'], 5)


class BindingProperty_Test(TestCase):
    class Class:
        @BindingProperty
        def attr(self):
            return self._attr

        @attr.setter
        def attr(self, value):
            self._attr = value

        @attr.deleter
        def attr(self):
            del self._attr

    def test(self):
        """
        Yes, this is a poor set of tests, but since I'm just slightly
        extending `property`, I thought it to be a waste of time to do a full
        suite of tests. I just wanted to do a quick check that all was
        working as planned.
        """
        instance = self.Class()

        # test get
        instance._attr = 5

        self.assertEqual(instance.attr, 5)

        self.assertIsInstance(self.Class.attr, UnboundAttribute)

        self.assertEqual(self.Class.attr(instance), 5)

        # test set
        instance.attr = 4

        self.assertEqual(instance.attr, 4)

        # test delete
        del instance.attr

        self.assertFalse('_attr' in instance.__dict__)


class ClassConstants_Test(TestCase):
    class Class(metaclass=withConstants(ATTR=5)):
        pass

    def test_not_accessible_from_instance(self):
        with self.assertRaises(AttributeError):
            self.Class().ATTR

    def test_constant_exists_and_is_correct(self):
        self.assertEqual(self.Class.ATTR, 5)

    def test_constant_cannot_be_set(self):
        with self.assertRaises(AttributeError):
            self.Class.ATTR = 4

    def test_constant_cannot_be_deleted(self):
        with self.assertRaises(AttributeError):
            del self.Class.ATTR
