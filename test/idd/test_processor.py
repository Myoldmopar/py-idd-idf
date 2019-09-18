import os
import sys
from six import StringIO
from unittest import TestCase, skipIf

from pyiddidf import settings
from pyiddidf.exceptions import ProcessingException
from pyiddidf.idd_processor import IDDProcessor


class TestIDDProcessingViaStream(TestCase):
    def test_proper_idd(self):
        idd_object = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD abcdef0000" + "\n" \
            r"" + "\n" \
            r"\group Simulation Parameters" + "\n" \
            r"Version," + "\n" \
            r"" + "\n" \
            r"\memo Specifies the EnergyPlus version of the IDF file." + "\n" \
            r"\unique-object" + "\n" \
            r"\format singleLine" + "\n" \
            r"A1 ; \field Version Identifier" + "\n" \
            r"\default 8.6" + "\n" \
            r""
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))

    def test_proper_idd_indented(self):
        idd_object = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD abcdef0001" + "\n" \
            r"\group Simulation Parameters" + "\n" \
            r"Version," + "\n" \
            r"      \memo Specifies the EnergyPlus version of the IDF file." + "\n" \
            r"      \unique-object" + "\n" \
            r"      \format singleLine" + "\n" \
            r"  A1; \field Version Identifier" + "\n" \
            r"      \default 8.6" + "\n"
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))

    def test_repeated_object_meta_idd(self):
        idd_object = \
            r"!IDD_Version 0.1.0" + "\n" \
            r"!IDD_BUILD abcdef0010" + "\n" \
            r"\group Simulation Parameters" + "\n" \
            r"" + "\n" \
            r"Version," + "\n" \
            r"     \memo Specifies the EnergyPlus version of the IDF file." + "\n" \
            r"     \memo Some additional memo line" + "\n" \
            r"     \unique-object" + "\n" \
            r"     \format singleLine" + "\n" \
            r"  A1 ; \field Version Identifier" + "\n" \
            r"      \default 8.6" + "\n" \
            r"" + "\n"
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))
        version_obj = ret_value.get_object_by_type("version")
        self.assertEquals(1, len(version_obj.fields))

    def test_new_reference_class_name(self):
        idd_object = \
            r"!IDD_Version 0.1.4" + "\n" \
            r"!IDD_BUILD abcded0810" + "\n" \
            r"\group Simulation Parameters" + "\n" \
            r"NewObject," + "\n" \
            r"  A1;  \field Name" + "\n" \
            r"       \required-field" + "\n" \
            r"       \type alpha" + "\n" \
            r"       \reference-class-name validBranchEquipmentTypes" + "\n" \
            r"       \reference validBranchEquipmentNames" + "\n"
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))
        version_obj = ret_value.get_object_by_type("NewObject")
        self.assertEquals(1, len(version_obj.fields))

    def test_single_line_obj_lookup(self):
        idd_object = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD sdkfj30934" + "\n" \
            r"Simulation Input;" + "\n" \
            r"\group Stuff" + "\n" \
            r"Version,A1;" + "\n"
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        bad_obj = ret_value.get_object_by_type("simulation input")
        self.assertTrue(bad_obj)

    def test_invalid_idd_obj_lookup(self):
        idd_object = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD abcdef0011" + "\n" \
            r"\group Stuff" + "\n" \
            r"Version,A1;" + "\n"
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        bad_obj = ret_value.get_object_by_type("noObjecT")
        self.assertIsNone(bad_obj)

    def test_invalid_idd_metadata_no_space(self):
        idd_string = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD abcdef0101" + "\n" \
            r"\group MyGroup" + "\n" \
            r"MyObject," + "\n" \
            r"  N1,  \field NumericFieldA" + "\n" \
            r"  N2;  \field NumericFieldB" + "\n" \
            r"       \autosizabled" + "\n"
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string).get_object_by_type('MyObject')

    def test_invalid_idd_metadata(self):
        idd_string = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD abcdef0110" + "\n" \
            r"\group MyGroup" + "\n" \
            r"MyObject," + "\n" \
            r"  N1,  \field NumericFieldA" + "\n" \
            r"  N2;  \field NumericFieldB" + "\n" \
            r"       \autosizQble" + "\n"
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string).get_object_by_type('MyObject')

    def test_missing_version(self):
        idd_string = \
            r"!IDD_BUILD abcdef0111" + "\n" \
            r"\group MyGroup" + "\n" \
            r"MyObject," + "\n" \
            r"  N1;  \field NumericFieldA" + "\n"
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_missing_build(self):
        idd_string = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"\group MyGroup" + "\n" \
            r"MyObject," + "\n" \
            r"  N1;  \field NumericFieldA" + "\n"
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_non_numeric_version(self):
        idd_string = \
            r"!IDD_Version X.Y.Z" + "\n" \
            r"!IDD_BUILD abcdef1000" + "\n" \
            r"\group MyGroup" + "\n" \
            r"MyObject," + "\n" \
            r"  N1;  \field NumericFieldA" + "\n"
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_bad_non_numeric_metadata(self):
        idd_string = \
            r"!IDD_Version 122.6.0" + "\n" \
            r"!IDD_BUILD abcdef1000" + "\n" \
            r"\group MyGroup" + "\n" \
            r"MyObject," + "\n" \
            r"  \min-fields Q" + "\n" \
            r"  N1;  \field NumericFieldA" + "\n"
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)


class TestIDDProcessingViaFile(TestCase):
    @skipIf(not settings.run_large_tests, "This is a large test that reads the entire idd")
    def test_valid_idd(self):  # pragma: no cover
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        idd_path = os.path.join(cur_dir, "..", "support_files", "Energy+.idd")
        processor = IDDProcessor()
        ret_value = processor.process_file_given_file_path(idd_path)
        self.assertEquals(57, len(ret_value.groups))
