from unittest import TestCase

from energyplus_iddidf.idd_objects import IDDGroup, IDDObject, IDDField


class TestIDDObjectRepresentations(TestCase):
    def test_all_strings(self):
        g = IDDGroup("group_name")
        self.assertIsInstance(str(g), str)
        o = IDDObject("object_name")
        self.assertIsInstance(str(o), str)
        f = IDDField("field_name")
        self.assertIsInstance(str(f), str)
