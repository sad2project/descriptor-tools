# coding=utf-8
from unittest import TestCase

import test_mocks as mocks
from descriptor_tools import get_descriptor_from, get_descriptor, name_of
from descriptor_tools.decorators import Binding
from descriptor_tools.find_descriptors import _find_descriptor

attrname = mocks.attrname


class Class:
    attr = mocks.Descriptor()
    attrname = 'attr'


class SubClass(Class):
    pass


class Get_Descriptor_Test(TestCase):
    def test_with_normal_descriptor(self):
        cls = type(mocks.ClassWithDescriptor(mocks.Descriptor()))

        result = get_descriptor(cls, attrname)

        self.assertIs(result, cls.__dict__[attrname])

    def test_with_binding_descriptor(self):
        cls = type(mocks.ClassWithDescriptor(Binding(mocks.Descriptor())))

        result = get_descriptor(cls, attrname)

        self.assertIs(result, cls.__dict__[attrname])

    def test_with_superclass(self):
        result = get_descriptor(SubClass, 'attr')

        self.assertIs(result, Class.__dict__['attr'])


class Get_Descriptor_From_Test(TestCase):
    def test_with_normal_descriptor(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())
        cls = type(instance)

        result = get_descriptor_from(instance, attrname)

        self.assertIs(result, cls.__dict__[attrname])

    def test_with_binding_descriptor(self):
        instance = mocks.ClassWithDescriptor(Binding(mocks.Descriptor()))
        cls = type(instance)

        result = get_descriptor_from(instance, attrname)

        self.assertIs(result, cls.__dict__[attrname])

    def test_with_superclass(self):
        result = get_descriptor_from(SubClass(), Class.attrname)

        self.assertIs(result, Class.__dict__[Class.attrname])


class _FindDescriptor_Test(TestCase):
    def test_with_normal_descriptor(self):
        cls = type(mocks.ClassWithDescriptor(mocks.Descriptor()))

        result = _find_descriptor(cls, attrname)

        self.assertIs(result, cls.__dict__[attrname])

    def test_with_binding_descriptor(self):
        cls = type(mocks.ClassWithDescriptor(Binding(mocks.Descriptor())))

        result = _find_descriptor(cls, attrname)

        self.assertIs(result, cls.__dict__[attrname])

    def test_with_superclass(self):
        result = _find_descriptor(SubClass, Class.attrname)

        self.assertIs(result, Class.__dict__[Class.attrname])





class Name_Of_Test(TestCase):
    def test_find_name_on_class(self):
        result = name_of(Class.attr, Class)

        self.assertEqual(result, Class.attrname)

    def test_find_name_on_sub_class(self):
        result = name_of(SubClass.attr, SubClass)

        self.assertEqual(result, SubClass.attrname)
