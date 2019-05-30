from unittest import TestCase

from descriptor_tools.storage import *


class DictStorageDescriptor:
    def __init__(self):
        self.storage = DictStorage()
        self.storage.desc = self

    def __set_name__(self, owner, name):
        self.storage.set_name(name)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.storage[instance]

    def __set__(self, instance, value):
        self.storage[instance] = value

    def __delete__(self, instance):
        del self.storage[instance]


class DictSutClass:
    attr = DictStorageDescriptor()

    def __init__(self):
        self.attr = 5


class DictStorage_Test(TestCase):
    def setUp(self):
        self.instance = DictSutClass()
        self.sut = DictSutClass.attr.storage

    def test_using_set_name_shortcuts_name_lookup(self):
        sut = DictStorage()

        sut.set_name("attr")

        self.assertEqual(sut.name(None), "attr")

    def test_skipping_set_name_uses_long_lookup(self):
        result = self.sut.name(self.instance)

        self.assertEqual(result, "attr")

    def test_skipping_set_name_caches_name_for_later_lookups(self):
        result1 = self.sut.name(DictSutClass)
        result2 = self.sut.name(None)

        self.assertEqual(result1, result2)

    def test_value_is_set_and_retrieved(self):
        self.assertEqual(5, self.instance.attr)

    def test_deletion(self):
        del self.instance.attr

        with self.assertRaises(AttributeError):
            _ = self.instance.attr


class InstStorageDescriptor:
    def __init__(self):
        self.storage = InstanceStorage()
        self.storage.desc = self

    def __set_name__(self, owner, name):
        self.storage.set_name(name)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.storage[instance]

    def __set__(self, instance, value):
        self.storage[instance] = value

    def __delete__(self, instance):
        del self.storage[instance]


class InstSutClass:
    attr = InstStorageDescriptor()

    def __init__(self):
        self.attr = 5


class InstanceStorage_Test(TestCase):
    def setUp(self):
        self.instance = InstSutClass()
        self.sut = InstSutClass.attr.storage

    def test_using_set_name_shortcuts_name_lookup(self):
        sut = DictStorage()

        sut.set_name("attr")

        self.assertEqual(sut.name(None), "attr")

    def test_skipping_set_name_uses_long_lookup(self):
        result = self.sut.name(self.instance)

        self.assertEqual(result, "attr")

    def test_skipping_set_name_caches_name_for_later_lookups(self):
        result1 = self.sut.name(DictSutClass)
        result2 = self.sut.name(None)

        self.assertEqual(result1, result2)

    def test_value_is_set_and_retrieved(self):
        self.assertEqual(5, self.instance.attr)

    def test_deletion(self):
        del self.instance.attr

        with self.assertRaises(AttributeError):
            _ = self.instance.attr


class NameManglers_Test(TestCase):
    def test_identity(self):
        self.assertEqual("someString", identity("someString", None))

    def test_protected(self):
        self.assertEqual("_someString", protected("someString", None))

    def test_hex_desc_id(self):
        hex_id = id_name_of(InstSutClass.attr)

        result = hex_desc_id("someString", InstSutClass.attr)

        self.assertEqual(hex_id, result)
