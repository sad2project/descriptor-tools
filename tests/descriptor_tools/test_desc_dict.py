from unittest import TestCase
from descriptor_tools import DescDict


class Mock:
    pass


class DescDict_Creation_Test(TestCase):
    def test_new_dict_is_empty(self):
        dict = DescDict()

        self.assertTrue(len(dict) == 0)

    def test_new_dict_created_from_old_dict(self):
        mc1 = Mock()
        mc2 = Mock()
        dict = DescDict({mc1: 1, mc2: 2})

        self.assertTrue(mc1 in dict)
        self.assertTrue(mc2 in dict)
        self.assertEqual(dict[mc1], 1)
        self.assertEqual(dict[mc2], 2)


class Unhashable:
    def __eq__(self, other):
        return self == other


class DescDict_ItemUse_Test(TestCase):
    def setUp(self):
        self.key = Unhashable()
        self.value = 1
        self.dict = DescDict()

    def test_add_and_get_item(self):
        self.dict[self.key] = self.value

        self.assertEqual(self.dict[self.key], self.value)

    def test_remove_and_contains_item(self):
        self.dict[self.key] = self.value

        self.assertTrue(self.key in self.dict)

        del self.dict[self.key]

        self.assertFalse(self.key in self.dict)


class Key:
    def __init__(self, value):
        self.value = value


class DescDict_Iteration_and_Clear_Test(TestCase):
    def setUp(self):
        self.key1 = Key(1)
        self.key2 = Key(2)
        self.key3 = Key(3)
        self.value1 = 1
        self.value2 = 2
        self.value3 = 3
        self.dict = DescDict({self.key1: self.value1, self.key2: self.value2,
                              self.key3: self.value3})

    def test_iter(self):
        keys = []
        for key in self.dict:
            keys.append(key)

        self.assertTrue(self.key1 in keys)
        self.assertTrue(self.key2 in keys)
        self.assertTrue(self.key3 in keys)
        self.assertEqual(len(self.dict), 3)

    def test_keys(self):
        keys = []
        for key in self.dict.keys():
            keys.append(key)

        self.assertTrue(self.key1 in keys)
        self.assertTrue(self.key2 in keys)
        self.assertTrue(self.key3 in keys)
        self.assertEqual(len(self.dict), 3)

    def test_values(self):
        values = []
        for value in self.dict.values():
            values.append(value)

        self.assertTrue(self.value1 in values)
        self.assertTrue(self.value2 in values)
        self.assertTrue(self.value3 in values)
        self.assertEqual(len(self.dict), 3)

    def test_items(self):
        items = []
        for item in self.dict.items():
            items.append(item)

        self.assertTrue((self.key1, self.value1) in items)
        self.assertTrue((self.key2, self.value2) in items)
        self.assertTrue((self.key3, self.value3) in items)
        self.assertEqual(len(items), 3)

    def test_clear(self):
        self.dict.clear()

        self.assertEqual(len(self.dict), 0)
        for _ in self.dict:
            self.fail()


class DescDict_Len_Test(TestCase):
    def setUp(self):
        self.key1 = Key(1)
        self.key2 = Key(2)
        self.key3 = Key(3)
        self.key4 = Key(4)

    def test_2(self):
        dict = DescDict({self.key1: 1, self.key2: 2})

        self.assertEqual(len(dict), 2)

    def test_4(self):
        dict = DescDict({self.key1: 1, self.key2: 2, self.key3: 3, self.key4: 4})
        self.assertEqual(len(dict), 4)


class StrMock:
    def __str__(self):
        return "KEY"
    def __repr__(self):
        return "StrMock()"


class DescDict_Str_and_Repr_Test(TestCase):
    def setUp(self):
        self.key1 = StrMock()
        self.key2 = StrMock()
        self.key3 = StrMock()
        self.key4 = StrMock()
        self.key5 = StrMock()
        self.key6 = StrMock()
        self.key7 = StrMock()

    def test_empty_str(self):
        dict = DescDict();

        self.assertEqual(str(dict), "DescDict{}")

    def test_empty_repr(self):
        dict = DescDict()

        self.assertEqual(repr(dict), "DescDict()")

    def test_single_str(self):
        dict = DescDict({self.key1: 1})

        self.assertEqual(str(dict), "DescDict{KEY: 1}")

    def test_single_repr(self):
        dict = DescDict({self.key1: 1})

        self.assertEqual(repr(dict), "DescDict({StrMock(): 1})")

    def test_six_str(self):
        dict = DescDict({
            self.key1: 1,
            self.key2: 1,
            self.key3: 1,
            self.key4: 1,
            self.key5: 1,
            self.key6: 1
        })

        # Because the order of the items coming back is unknown, I had to use
        # keys that would look the same for each instance (values too)
        self.assertEqual(str(dict), "DescDict{KEY: 1, KEY: 1, KEY: 1, KEY: 1, KEY: 1, KEY: 1}")

    def test_six_repr(self):
        dict = DescDict({
            self.key1: 1,
            self.key2: 1,
            self.key3: 1,
            self.key4: 1,
            self.key5: 1,
            self.key6: 1
        })

        self.assertEqual(repr(dict), "DescDict({StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1})")

    def test_seven_str(self):
        dict = DescDict({
            self.key1: 1,
            self.key2: 1,
            self.key3: 1,
            self.key4: 1,
            self.key5: 1,
            self.key6: 1,
            self.key7: 1
        })

        self.assertEqual(str(dict), "DescDict{KEY: 1, KEY: 1, KEY: 1, KEY: 1, KEY: 1, KEY: 1, ...}")

    def test_seven_repr(self):
        dict = DescDict({
            self.key1: 1,
            self.key2: 1,
            self.key3: 1,
            self.key4: 1,
            self.key5: 1,
            self.key6: 1,
            self.key7: 1
        })

        self.assertEqual(repr(dict), "DescDict({StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1, StrMock(): 1})")

class DescDict_Update_Test(TestCase):
    def test_update_all_new_dict(self):
        dict = DescDict()
        updater = {Key(1): 1, Key(2): 2}

        dict.update(updater)

        self.assertEqual(dict, updater)

    def test_update_overlap_dict(self):
        key1 = Key(1)
        key3 = Key(3)
        dict = DescDict({key1: 1, key3: 3})
        updater = {key1: 2, Key(2): 2}

        dict.update(updater)

        updater[key3] = 3  # make `updater` match what `dict` should be
        self.assertEqual(dict, updater)

    def test_update_all_new_iterable(self):
        key1 = Key(1)
        key2 = Key(2)
        dict = DescDict()
        updater = ((key1, 1), (key2, 2))

        dict.update(updater)

        final = DescDict({key1: 1, key2: 2})
        self.assertEqual(dict, final)

    def test_update_overlap_iterable(self):
        key1 = Key(1)
        key2 = Key(2)
        key3 = Key(3)
        dict = DescDict({key1: 1, key3: 3})
        updater = ((key1, 2), (key2, 2))

        dict.update(updater)

        final = DescDict({key1: 2, key2: 2, key3: 3})
        self.assertEqual(dict, final)


class DescDict_Finalizer_Test(TestCase):
    """
    Only works in a Python implementation that uses simple reference counting
    garbage collecting. Otherwise, there's no telling how long it may take for
    the garbage collector to clean up the instance
    """
    def test_finalize(self):
        dict = DescDict()
        key = Key(1)

        dict[key] = 1

        self.assertEqual(len(dict), 1)

        del key

        self.assertEqual(len(dict), 0)
