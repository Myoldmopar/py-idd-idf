from io import StringIO
import os
from unittest import TestCase, skipIf

from energyplus_iddidf import settings
from energyplus_iddidf.exceptions import ProcessingException
from energyplus_iddidf.idd_processor import IDDProcessor


class TestIDDProcessingViaStream(TestCase):
    def test_proper_idd(self):
        idd_object = """
!IDD_Version 1.2.0
!IDD_BUILD abcdef0000
\\group Simulation Parameters

Version,
      \\memo Specifies the EnergyPlus version of the IDF file.
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\default 8.6

"""
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))

    def test_proper_idd_indented(self):
        idd_object = """
    !IDD_Version 1.2.0
    !IDD_BUILD abcdef0001
    \\group Simulation Parameters

    Version,
          \\memo Specifies the EnergyPlus version of the IDF file.
          \\unique-object
          \\format singleLine
      A1 ; \\field Version Identifier
          \\default 8.6
    """
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))

    def test_repeated_object_meta_idd(self):
        idd_object = """
!IDD_Version 0.1.0
!IDD_BUILD abcdef0010
\\group Simulation Parameters

Version,
      \\memo Specifies the EnergyPlus version of the IDF file.
      \\memo Some additional memo line
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\default 8.6

"""
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))
        version_obj = ret_value.get_object_by_type("version")
        self.assertEquals(1, len(version_obj.fields))

    def test_new_reference_class_name(self):
        idd_object = """
!IDD_Version 0.1.4
!IDD_BUILD abcded0810
\\group Simulation Parameters
NewObject,
  A1;  \\field Name
       \\required-field
       \\type alpha
       \\reference-class-name validBranchEquipmentTypes
       \\reference validBranchEquipmentNames
        """
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(1, len(ret_value.groups[0].objects))
        version_obj = ret_value.get_object_by_type("NewObject")
        self.assertEquals(1, len(version_obj.fields))

    def test_single_line_obj_lookup(self):
        idd_object = """
!IDD_Version 1.2.0
!IDD_BUILD abcdef0011
Simulation Input;
\\group Stuff
Version,A1;
"""
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        bad_obj = ret_value.get_object_by_type("simulation input")
        self.assertTrue(bad_obj)

    def test_invalid_idd_obj_lookup(self):
        idd_object = """
!IDD_Version 1.2.0
!IDD_BUILD abcdef0100
\\group Stuff
Version,A1;
"""
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        bad_obj = ret_value.get_object_by_type("noObjecT")
        self.assertIsNone(bad_obj)

    def test_invalid_idd_metadata_no_space(self):
        idd_string = """
        !IDD_Version 1.2.0
        !IDD_BUILD abcdef0101
        \\group MyGroup
        MyObject,
          N1,  \\field NumericFieldA
          N2;  \\field NumericFieldB
               \\autosizabled
                """
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string).get_object_by_type('MyObject')

    def test_invalid_idd_metadata(self):
        idd_string = """
        !IDD_Version 1.2.0
        !IDD_BUILD abcdef0110
        \\group MyGroup
        MyObject,
          N1,  \\field NumericFieldA
          N2;  \\field NumericFieldB
               \\autosizQble
                """
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string).get_object_by_type('MyObject')

    def test_missing_version(self):
        idd_string = """
        !IDD_BUILD abcdef0111
        \\group MyGroup
        MyObject,
          N1;  \\field NumericFieldA
        """
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_missing_build(self):
        idd_string = """
        !IDD_Version 1.2.0
        \\group MyGroup
        MyObject,
          N1;  \\field NumericFieldA
        """
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_non_numeric_version(self):
        idd_string = """
        !IDD_Version X.Y.Z
        !IDD_BUILD abcdef1000
        \\group MyGroup
        MyObject,
          N1;  \\field NumericFieldA
        """
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_bad_non_numeric_metadata(self):
        idd_string = """
        !IDD_Version 122.6.0
        !IDD_BUILD abcdef1000
        \\group MyGroup
        MyObject,
          \\min-fields Q
          N1;  \\field NumericFieldA
        """
        with self.assertRaises(ProcessingException):
            IDDProcessor().process_file_via_string(idd_string)

    def test_trailing_an_value(self):
        idd_object = """
    !IDD_Version 1.2.8
    !IDD_BUILD abcdef1001
    \\group Simulation Parameters

    Version,
          \\memo Specifies the EnergyPlus version of the IDF file.
          \\unique-object
          \\format singleLine
      A1 ; 

    MyObject,
          \\min-fields 1
          N1;
    """
        processor = IDDProcessor()
        ret_value = processor.process_file_via_stream(StringIO(idd_object))
        self.assertEquals(1, len(ret_value.groups))
        self.assertEquals(2, len(ret_value.groups[0].objects))


class TestIDDProcessingViaFile(TestCase):
    @skipIf(not settings.run_large_tests, "This is a large test that reads the entire idd")
    def test_valid_idd(self):  # pragma: no cover
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        idd_path = os.path.join(cur_dir, "", "support_files", "Energy+.idd")
        processor = IDDProcessor()
        ret_value = processor.process_file_given_file_path(idd_path)
        self.assertEquals(57, len(ret_value.groups))
