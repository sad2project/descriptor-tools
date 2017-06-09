# coding=utf-8
from unittest import TestCase
from tests.descriptor_tools.test_mocks import Descriptor
from descriptor_tools import UnboundAttribute
from descriptor_tools.decorators import DescriptorDecoratorBase


class Class:
    descAttr = Descriptor()


class UnboundAttr_Test(TestCase):
    def setUp(self):
        self.unboundattr = UnboundAttribute(Class.descAttr, Class)

    def test_creation(self):
        instance = Class()
        instance.descAttr = 5

        result = self.unboundattr(instance)

        self.assertEqual(result, 5)

    def test_attribute_forwarding(self):
        self.assertIs(self.unboundattr.__get__.__func__,
                      Descriptor.__get__)
        self.assertIs(self.unboundattr.__set__.__func__,
                      Descriptor.__set__)

    def test_setter(self):
        instance = Class()

        self.unboundattr.set(instance, 5)

        self.assertEqual(instance.descAttr, 5)

    def test_deleter(self):
        instance = Class()
        instance.descAttr = 5

        self.unboundattr.delete(instance)

        self.assertFalse(hasattr(instance, "descAttr"))

class UnboundAttr_LiftDescriptor_Test(TestCase):
    def setUp(self):
        unboundattr = UnboundAttribute(Class.descAttr, Class)
        self.wrapper_descriptor = DescriptorDecoratorBase(Class.descAttr)

        self.new_unboundattr = unboundattr.lift_descriptor(self.wrapper_descriptor)

    def test_lift_descriptor_new_descriptor(self):
        unboundattr = UnboundAttribute(Class.descAttr, Class)
        wrapper_descriptor = DescriptorDecoratorBase(Class.descAttr)

        new_unboundattr = unboundattr.lift_descriptor(wrapper_descriptor)

        self.assertEqual(new_unboundattr.descriptor, wrapper_descriptor)

    def test_lift_descriptor_set(self):
        instance = Class()
        unboundattr = UnboundAttribute(Class.descAttr, Class)
        wrapper_descriptor = DescriptorDecoratorBase(Class.descAttr)

        new_unboundattr = unboundattr.lift_descriptor(wrapper_descriptor)
        new_unboundattr.set(instance, 5)

        self.assertEqual(instance.descAttr, 5)


class AnotherClass:
    desc = Descriptor()


class UnboundAttr_Strings_Test(TestCase):
    def test_str_Class(self):
        unboundattr = UnboundAttribute(Class.descAttr, Class)

        self.assertEqual(str(unboundattr),
                         "Unbound Attribute 'Class.descAttr'")

    def test_str_AnotherClass(self):
        unboundattr = UnboundAttribute(AnotherClass.desc, AnotherClass)

        self.assertEqual(str(unboundattr),
                         "Unbound Attribute 'AnotherClass.desc'")

    def test_repr_Class(self):
        unboundattr = UnboundAttribute(Class.descAttr, Class)
        descrep = repr(Class.descAttr)
        classrep = repr(Class)

        self.assertEqual(repr(unboundattr),
                         'UnboundAttribute(' + descrep + ', ' + classrep + ')')
