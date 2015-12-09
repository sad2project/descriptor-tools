from unittest import TestCase
import tests.descriptor_tools.test_mocks as mocks
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


class Get_Descriptor_From_Test(TestCase):

    def test_with_normal_descriptor_unspecified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        result = get_descriptor_from(instance, "attr")

        self.assertIsInstance(result, mocks.Descriptor)

    def test_with_binding_descriptor_unspecified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor_from(instance, "attr")

        self.assertIsInstance(result, mocks.Binding)

    def test_with_normal_descriptor_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        result = get_descriptor_from(instance, "attr", binding=False)

        self.assertIsInstance(result, mocks.Descriptor)

    def test_with_binding_descriptor_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor_from(instance, "attr", binding=True)

        self.assertIsInstance(result, mocks.Binding)

    def test_with_normal_descriptor_incorrectly_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        with self.assertRaises(AttributeError):
            get_descriptor_from(instance, "attr", binding=True)

    def test_with_binding_descriptor_incorrectly_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor_from(instance, "attr", binding=False)

        self.assertIsInstance(result, mocks.UnboundAttribute)


attrname = mocks.attrname
class Setters_Test(TestCase):

    def test_attr_setting_with_attr(self):
        instance = mocks.ClassWithOutDescriptor()

        Setters.attr(instance, attrname, 0)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_attr_setting_with_descriptor(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        Setters.attr(instance, attrname, 0)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_basic_setting(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        Setters.basic(instance, attrname, 0, binding=False)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_forced_setting(self):
        instance = mocks.ClassWithDescriptor(mocks.ForcedSet(mocks.Descriptor()))

        Setters.forced(instance, attrname, 0, binding=False)

        self.assertEqual(getattr(instance, attrname), 0)

    def test_secret_setting(self):
        instance = mocks.ClassWithDescriptor(mocks.SecretSet(mocks.Descriptor()))

        Setters.secret(instance, attrname, 0, binding=False)

        self.assertEqual(getattr(instance, attrname), 0)
