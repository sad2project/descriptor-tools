# coding=utf-8
from unittest import TestCase
import tests.descriptor_tools.test_mocks as mocks
from descriptor_tools.decorators import ForcedSet, SecretSet, Binding
from descriptor_tools.set_attrs import *

prefix = "_"
postfix = "_attr"
testString = "aString"


class Mangle_Name_Test(TestCase):

    def test_defaults(self):
        self.assertEqual(mangle_name(testString), testString)

    def test_prefix(self):
        self.assertEqual(mangle_name(testString, prefix=prefix),
                         prefix + testString)

    def test_postfix(self):
        self.assertEqual(mangle_name(testString, postfix=postfix),
                         testString + postfix)

    def test_both(self):
        self.assertEqual(mangle_name(testString, prefix=prefix, postfix=postfix),
                         prefix + testString + postfix)


class Name_Mangler_Test(TestCase):

    def test_defaults(self):
        mangle = NameMangler()
        self.assertEqual(mangle(testString), testString)

    def test_prefix(self):
        mangle = NameMangler(prefix=prefix)
        self.assertEqual(mangle(testString), prefix + testString)

    def test_postfix(self):
        mangle = NameMangler(postfix=postfix)
        self.assertEqual(mangle(testString), testString + postfix)

    def test_both(self):
        mangle = NameMangler(prefix=prefix, postfix=postfix)
        self.assertEqual(mangle(testString), prefix + testString + postfix)


class Set_On_Test(TestCase):

    class Class:
        pass

    def test_set_on(self):
        instance = Set_On_Test.Class()
        attr = "someAttribute"
        value = 0

        set_on(instance, attr, value)

        self.assertEqual(instance.__dict__[attr], value)


attrname = mocks.attrname


class Setters_Test(TestCase):

    def test_basic_setting(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        Setter.basic(instance, attrname, 0, binding=False)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_forced_setting(self):
        instance = mocks.ClassWithDescriptor(ForcedSet(mocks.Descriptor()))

        Setter.forced(instance, attrname, 0, binding=False)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_secret_setting(self):
        instance = mocks.ClassWithDescriptor(SecretSet(mocks.Descriptor()))

        Setter.secret(instance, attrname, 0, binding=False)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_basic_setting_with_binding_descriptor(self):
        instance = mocks.ClassWithDescriptor(Binding(mocks.Descriptor()))

        Setter.basic(instance, attrname, 0, binding=True)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_forced_setting_with_binding_descriptor(self):
        instance = mocks.ClassWithDescriptor(ForcedSet(Binding(
                mocks.Descriptor())))

        Setter.forced(instance, attrname, 0, binding=True)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_secret_setting_with_binding_descriptor(self):
        instance = mocks.ClassWithDescriptor(SecretSet(Binding(
                mocks.Descriptor())))

        Setter.secret(instance, attrname, 0, binding=True)

        self.assertEqual(getattr(instance, attrname), 0)


class SetAttribute_Test(TestCase):
    pass  # TODO continue


class AttributeSetter_Test(TestCase):
    pass  # TODO
