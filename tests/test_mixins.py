# coding=utf-8
from unittest import TestCase

import test_mocks as mocks
from descriptor_tools import DescDict, id_name_of
from descriptor_tools.mixins import (Getters,
                                     Storage,
                                     Setters)


class Getter_Binding_Test(TestCase):
    class Desc(Getters.Binding):
        def __init__(self):
            self.storage = DescDict()

        def _get(self, instance):
            return self.storage[instance]

    def setUp(self):
        self.desc = self.Desc()
        self.instance = mocks.ClassWithDescriptor(self.desc)
        self.Class = type(self.instance)

    def test_get_from_class_is_unbound_descriptor(self):
        result = self.Class.attr

        self.assertIsInstance(result, self.Desc)

    def test_get_from_class_has_correct_descriptor(self):
        result = self.Class.attr

        self.assertIs(result, self.desc)

    def test_get_from_instance(self):
        self.desc.storage[self.instance] = 5
        result = self.instance.attr

        self.assertEqual(result, 5)


class Getter_SelfReturning_Test(TestCase):
    class Desc(Getters.SelfReturning):
        def _get(self, instance):
            return 5

    def setUp(self):
        self.desc = self.Desc()
        self.instance = mocks.ClassWithDescriptor(self.desc)
        self.Class = type(self.instance)

    def test_get_from_class_is_desc(self):
        result = self.desc.__get__(None, self.Class)

        self.assertIs(result, self.desc)

    def test_get_from_instance_is_value(self):
        result = self.desc.__get__(self.instance, self.Class)

        self.assertEqual(result, 5)


class Storage_DescDict_Test(TestCase):
    class Class:
        pass

    def setUp(self):
        self.mixin = Storage.DescDict()
        self.instance = self.Class()

    def test_uses_DescDict_storage(self):
        self.assertIsInstance(self.mixin.storage, DescDict)

    def test_get_retrieves_from_storage(self):
        self.mixin.storage[self.instance] = 5

        result = self.mixin._get(self.instance)

        self.assertEqual(result, 5)

    def test_set_applies_to_storage(self):
        self.mixin._set(self.instance, 5)

        result = self.mixin._get(self.instance)

        self.assertEqual(result, 5)

    def test_delete_applies_to_storage(self):
        self.mixin.storage[self.instance] = 5

        self.mixin._delete(self.instance)

        self.assertFalse(self.instance in self.mixin.storage)


class Storage_KeyByName_UsingPreAndPostFix_Test(TestCase):
    class Class:
        attr = Storage.KeyByName(prefix='_', postfix='_')

    def setUp(self):
        self.mixin = self.Class.attr
        self.instance = self.Class()

    def test_name_getter(self):
        result = self.mixin._name(self.instance)

        self.assertEqual(result, '_attr_')

    def test_name_getter_works_multiple_times(self):
        """
        Because OnInstance tries to cache the _name, I want to make sure
        subsequent lookups still work
        """
        result1 = self.mixin._name(self.instance)
        result2 = self.mixin._name(self.instance)

        self.assertEqual(result1, result2)

    def test_get_retrieves_from_instance(self):
        self.instance._attr_ = 5

        result = self.mixin._get(self.instance)

        self.assertEqual(result, 5)

    def test_set_applies_to_instance(self):
        self.mixin._set(self.instance, 5)

        result = self.instance._attr_

        self.assertEqual(result, 5)

    def test_delete_applies_to_instance(self):
        self.instance._attr_ = 5

        self.mixin._delete(self.instance)

        self.assertFalse(hasattr(self.instance, '_attr_'))


class Storage_KeyByName_UsingName_Test(TestCase):
    class Class:
        attr = Storage.KeyByName(name='subattr')

    def setUp(self):
        self.mixin = self.Class.attr
        self.instance = self.Class()

    def test_name_getter(self):
        result = self.mixin._name(self.instance)

        self.assertEqual(result, 'subattr')

    def test_get_retrieves_from_instance(self):
        self.instance.subattr = 5

        result = self.mixin._get(self.instance)

    def test_set_applies_to_instance(self):
        self.mixin._set(self.instance, 5)

        result = self.instance.subattr

        self.assertEqual(result, 5)

    def test_delete_applies_to_instance(self):
        self.instance.subattr = 5

        self.mixin._delete(self.instance)

        self.assertFalse(hasattr(self.instance, 'subattr'))


class Desc(Getters.SelfReturning, Storage.KeyByName):
    def __set__(self, instance, value):
        self._set(instance, value)

    def __delete__(self, instance):
        self._delete(instance)

class Storage_KeyByName_UsingSameName_AsDescriptor_Test(TestCase):
    class Class:
        attr = Desc()

    def setUp(self):
        self.desc = self.Class.attr
        self.instance = self.Class()

    def test_name_getter(self):
        result = self.desc._name(self.instance)

        self.assertEqual(result, 'attr')

    def test_get_retrieves_from_instance(self):
        self.instance.__dict__['attr'] = 5

        result = self.instance.attr

        self.assertEqual(result, 5)

    def test_set_applies_to_instance(self):
        self.instance.attr = 5

        result = self.desc._get(self.instance)

        self.assertEqual(result, 5)

    def test_delete_applies_to_instance(self):
        self.desc._set(self.instance, 5)

        del self.instance.attr

        self.assertFalse('attr' in self.instance.__dict__)


class Desc(Getters.SelfReturning, Storage.KeyById):
    def __set__(self, instance, value):
        self._set(instance, value)

    def __delete__(self, instance):
        self._delete(instance)

class Storage_KeyById_Test(TestCase):
    class Class:
        attr = Desc()

    def setUp(self):
        self.desc = self.Class.attr
        self.instance = self.Class()
        self.attrName = self.desc._name

    def test_name_is_correct(self):
        expected = id_name_of(self.desc)

        self.assertEqual(self.attrName, expected)

    def test_get(self):
        setattr(self.instance, self.attrName, 5)

        result = self.desc.__get__(self.instance, self.Class)

        self.assertEqual(result, 5)

    def test_set_item_exists(self):
        self.desc.__set__(self.instance, 5)

        self.assertTrue(hasattr(self.instance, self.desc._name))

    def test_set_item_correct(self):
        self.desc.__set__(self.instance, 5)

        self.assertEqual(getattr(self.instance, self.desc._name), 5)

    def test_delete(self):
        self.instance.__dict__[self.attrName] = 5

        self.desc.__delete__(self.instance)

        self.assertFalse(hasattr(self.instance, self.desc._name))


class Desc(Getters.SelfReturning, Setters.Forced, Storage.DescDict):
    pass

class Setters_Forced_Test(TestCase):
    class Class:
        attr = Desc()

    def setUp(self):
        self.desc = self.Class.attr
        self.instance = self.Class()

    def test_unforced_fails(self):
        with self.assertRaises(AttributeError):
            self.desc.__set__(self.instance, 5)

    def test_forced_works(self):
        self.desc.__set__(self.instance, 5, force=True)

        self.assertEqual(self.instance.attr, 5)


class Desc(Getters.SelfReturning, Setters.Secret, Storage.DescDict):
    pass

class Setters_Secret_Test(TestCase):
    class Class:
        attr = Desc()

    def setUp(self):
        self.desc = self.Class.attr
        self.instance = self.Class()

    def test_normal_set_fails(self):
        with self.assertRaises(AttributeError):
            self.desc.__set__(self.instance, 5)

    def test_secret_set_works(self):
        self.desc.set(self.instance, 5)

        self.assertEqual(self.instance.attr, 5)
