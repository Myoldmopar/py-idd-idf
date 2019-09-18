import unittest

from six import StringIO

from pyiddidf.idd_processor import IDDProcessor
from pyiddidf.idf_objects import IDFObject, ValidationIssue
from pyiddidf.idf_processor import IDFProcessor


class TestIDFObject(unittest.TestCase):
    def test_valid_object(self):
        tokens = ["Objecttype", "object_name", "something", "", "last field with space"]
        obj = IDFObject(tokens)
        self.assertEquals("Objecttype", obj.object_name)
        self.assertEquals(4, len(obj.fields))
        obj.object_string()
        s = StringIO()
        obj.write_object(s)
        expected_string = """Objecttype,
  object_name,             !-%20
  something,               !-%20
  ,                        !-%20
  last field with space;   !-%20
"""
        self.assertEqual(expected_string.replace('%20', ' '), s.getvalue())
        tokens = ["Objecttypenofields"]
        obj = IDFObject(tokens)
        self.assertEquals("Objecttypenofields", obj.object_name)
        obj.object_string()
        obj.write_object(s)


class TestSingleLineIDFValidation(unittest.TestCase):
    def test_valid_single_token_object_no_idd(self):
        tokens = ["SingleLineObject"]
        obj = IDFObject(tokens)
        self.assertEquals("SingleLineObject", obj.object_name)
        self.assertEquals(0, len(obj.fields))
        s = obj.object_string()
        self.assertEquals("SingleLineObject;\n", s)

    def test_valid_single_token_object_with_idd(self):
        idd_string = \
            r"!IDD_Version 1.2.0" + "\n" \
            r"!IDD_BUILD abcdef1001" + "\n" \
            r"\group MyGroup" + "\n" \
            r"SingleLineObject;" + "\n"
        idd_object = IDDProcessor().process_file_via_string(idd_string).get_object_by_type('SingleLineObject')
        tokens = ["SingleLineObject"]
        obj = IDFObject(tokens)
        self.assertEquals("SingleLineObject", obj.object_name)
        self.assertEquals(0, len(obj.fields))
        s = obj.object_string(idd_object)
        self.assertEquals("SingleLineObject;\n", s)


class TestIDFFieldValidation(unittest.TestCase):
    def setUp(self):
        idd_string = \
            r"!IDD_Version 12.9.0" + "\n" \
            r"!IDD_BUILD abcdef1010" + "\n" \
            r"\group MyGroup" + "\n" \
            r"Version," + "\n" \
            r"  A1;  \field VersionID" + "\n" \
            r"" + "\n" \
            r"MyObject," + "\n" \
            r"  N1,  \field NumericFieldA" + "\n" \
            r"       \minimum 0" + "\n" \
            r"       \maximum 2" + "\n" \
            r"       \required-field" + "\n" \
            r"  N2,  \field NumericFieldB" + "\n" \
            r"       \minimum> 0" + "\n" \
            r"       \maximum< 2" + "\n" \
            r"       \autosizable" + "\n" \
            r"  N3;  \field NumericFieldB" + "\n" \
            r"       \minimum> 0" + "\n" \
            r"       \maximum< 2" + "\n" \
            r"       \autocalculatable" + "\n"
        self.idd_structure = IDDProcessor().process_file_via_string(idd_string)
        self.idd_object = self.idd_structure.get_object_by_type('MyObject')

    def test_valid_idf_object(self):
        idf_string = "Version,12.9;MyObject,1,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_valid_idf_object_but_None_idd_object(self):
        idf_string = "Version,12.9;MyObject,1,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(None)
        self.assertEqual(len(issues), 0)

    def test_missing_version(self):
        # Missing version is now supported
        idf_string = "MyObject,1,1,1;"
        idf_processor = IDFProcessor().process_file_via_string(idf_string)
        version_object = idf_processor.get_idf_objects_by_type('Version')
        self.assertEqual(0, len(version_object))

    def test_non_numeric(self):
        idf_string = "Version,12.9;MyObject,A,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_blank_numeric(self):
        idf_string = "Version,12.9;MyObject,1,,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_non_numeric_but_autosize(self):
        idf_string = "Version,12.9;MyObject,1,AutoSize,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_non_numeric_but_autocalculatable(self):
        idf_string = "Version,12.9;MyObject,1,1,AutoCalculate;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_non_numeric_autosize_but_not_allowed(self):
        idf_string = "Version,12.9;MyObject,AutoSize,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_non_numeric_autocalculate_but_not_allowed(self):
        idf_string = "Version,12.9;MyObject,AutoCalculate,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_numeric_too_high_a(self):
        idf_string = "Version,12.9;MyObject,3,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_numeric_too_high_b(self):
        idf_string = "Version,12.9;MyObject,1,2,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_numeric_too_low_a(self):
        idf_string = "Version,12.9;MyObject,-1,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_numeric_too_low_b(self):
        idf_string = "Version,12.9;MyObject,1,0,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_missing_required_field(self):
        idf_string = "Version,12.9;MyObject,,1,1;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 1)

    def test_whole_idf_valid(self):
        idf_string = "Version,12.9;MyObject,1,1,1;MyObject,1,1,1;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 0)

    def test_whole_idf_valid_with_comments(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,1,1,1;" + "\n" \
            r"! ME COMMENT" + "\n" \
            r"MyObject,1,1,1;" + "\n"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 0)
        s_idf = idf_structure.whole_idf_string(self.idd_structure)
        print(s_idf)
        self.assertTrue('ME COMMENT' in s_idf)

    def test_whole_idf_one_invalid(self):
        idf_string = "Version,12.9;MyObject,-1,1,1;MyObject,1,1,1;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 1)

    def test_whole_idf_two_invalid(self):
        idf_string = "Version,12.9;MyObject,-1,1,1;MyObject,-1,1,1;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 2)


class TestIDFObjectValidation(unittest.TestCase):
    def setUp(self):
        idd_string = \
            r"!IDD_Version 13.9.0" + "\n" \
            r"!IDD_BUILD abcdef1018" + "\n" \
            r"\group MyGroup" + "\n" \
            r"Version," + "\n" \
            r"  A1;  \field VersionID" + "\n" \
            r"" + "\n" \
            r"MyObject," + "\n" \
            r"       \min-fields 5" + "\n" \
            r"  A1,  \field Name" + "\n" \
            r"       \required-field" + "\n" \
            r"  A2,  \field Zone Name" + "\n" \
            r"       \required-field" + "\n" \
            r"  N1,  \field A" + "\n" \
            r"       \required-field" + "\n" \
            r"       \units m" + "\n" \
            r"  N2,  \field B" + "\n" \
            r"       \required-field" + "\n" \
            r"  N3;  \field C" + "\n" \
            r"       \default 0.8" + "\n" \
            r"       \required-field" + "\n"
        self.idd_structure = IDDProcessor().process_file_via_string(idd_string)
        self.idd_object = self.idd_structure.get_object_by_type('MyObject')

    def test_valid_fully_populated_idf_object(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,Name,ZoneName,1,2,3;" + "\n"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_valid_defaulted_missing_idf_object(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,Name,ZoneName,1,2;" + "\n"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_valid_defaulted_blank_idf_object(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,Name,ZoneName,1,2,;" + "\n"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)

    def test_invalid_idf_object_required_field_no_default(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,Name,ZoneName,1;" + "\n"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 2)

    def test_units_are_persisted_when_writing(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,Name,ZoneName,1,2,3;" + "\n"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('MyObject')[0]
        issues = idf_object.validate(self.idd_object)
        self.assertEqual(len(issues), 0)
        os = idf_object.object_string(self.idd_object)
        self.assertIn('{m}', os)


class TestWritingWholeIDF(unittest.TestCase):

    def setUp(self):
        idd_string = \
            r"!IDD_Version 13.9.0" + "\n" \
            r"!IDD_BUILD abcdef1018" + "\n" \
            r"\group MyGroup" + "\n" \
            r"Version," + "\n" \
            r"  A1;  \field VersionID" + "\n" \
            r"" + "\n" \
            r"MyObject," + "\n" \
            r"       \min-fields 5" + "\n" \
            r"  A1,  \field Name" + "\n" \
            r"       \required-field" + "\n" \
            r"  A2,  \field Zone Name" + "\n" \
            r"       \required-field" + "\n" \
            r"  N1,  \field A" + "\n" \
            r"       \required-field" + "\n" \
            r"       \units m" + "\n" \
            r"  N2,  \field B" + "\n" \
            r"       \required-field" + "\n" \
            r"  N3;  \field C" + "\n" \
            r"       \default 0.8" + "\n" \
            r"       \required-field" + "\n"
        self.idd_structure = IDDProcessor().process_file_via_string(idd_string)
        self.idd_object = self.idd_structure.get_object_by_type('MyObject')

    def test_units_are_persisted_when_writing(self):
        idf_string = \
            r"Version,12.9;" + "\n" \
            r"MyObject,Name,ZoneName,1,2,3;" + "\n"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 0)
        import tempfile
        file_object = tempfile.NamedTemporaryFile()
        idf_structure.write_idf(file_object.name, self.idd_structure)


class TestIDFStructureValidation(unittest.TestCase):
    def setUp(self):
        idd_string = \
            r"!IDD_Version 8.1.0" + "\n" \
            r"!IDD_BUILD abcdef1011" + "\n" \
            r"\group MyGroup" + "\n" \
            r"Version," + "\n" \
            r"  A1;  \field VersionID" + "\n" \
            r"" + "\n" \
            r"ObjectU," + "\n" \
            r"  \unique-object" + "\n" \
            r"  \required-object" + "\n" \
            r"  N1;  \field NumericFieldA" + "\n" \
            r"" + "\n" \
            r"OtherObject," + "\n" \
            r"  N1;  \field Again" + "\n"
        self.idd_structure = IDDProcessor().process_file_via_string(idd_string)

    def test_valid_object(self):
        idf_string = "Version,12.9;ObjectU,1;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 0)

    def test_missing_required_object(self):
        idf_string = "Version,12.9;OtherObject,1;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 1)

    def test_multiple_unique_object(self):
        idf_string = "Version,12.9;ObjectU,1;ObjectU,1;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        issues = idf_structure.validate(self.idd_structure)
        self.assertEqual(len(issues), 1)

    def test_single_line_validation(self):
        idd_string = \
            r"!IDD_Version 56.1.0" + "\n" \
            r"!IDD_BUILD abcdef1011" + "\n" \
            r"\group MyGroup" + "\n" \
            r"Version," + "\n" \
            r"A1; \field VersionID" + "\n" \
            r"" + "\n" \
            r"Object;" + "\n"
        idd_object = IDDProcessor().process_file_via_string(idd_string).get_object_by_type('Object')
        idf_string = "Version,23.1;Object;"
        idf_object = IDFProcessor().process_file_via_string(idf_string).get_idf_objects_by_type('Object')[0]
        issues = idf_object.validate(idd_object)
        self.assertEqual(len(issues), 0)


class TestGlobalSwap(unittest.TestCase):
    def setUp(self):
        idd_string = \
            r"!IDD_Version 87.11.0" + "\n" \
            r"!IDD_BUILD abcdef1011" + "\n" \
            r"\group MyGroup" + "\n" \
            r"Version," + "\n" \
            r"   A1;  \field VersionID" + "\n" \
            r"" + "\n" \
            r"ObjectU," + "\n" \
            r"   A1;  \field My field name" + "\n"
        self.idd_structure = IDDProcessor().process_file_via_string(idd_string)

    def test_swapping(self):
        idf_string = "Version,87.11;ObjectU,MyFirstKey;"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        idf_structure.global_swap({"MyFirstKey": "MySecondKey"})
        idf_object = idf_structure.get_idf_objects_by_type("ObjectU")[0]
        self.assertIn("MySecondKey", idf_object.fields)

    def test_swapping_including_comment(self):
        idf_string = \
            r"Version," + "\n" \
            r" 87.11;" + "\n" \
            r"ObjectU," + "\n" \
            r" MyFirstKey;" + "\n" \
            r"! Comments here" + "\n" \
            r"ObjectU," + "\n" \
            r" NotMyFirstKey;" + "\n"
        idf_structure = IDFProcessor().process_file_via_string(idf_string)
        idf_structure.global_swap({"MyFirstKey": "MySecondKey"})
        idf_object = idf_structure.get_idf_objects_by_type("ObjectU")[0]
        self.assertIn("MySecondKey", idf_object.fields)


class TestValidationIssue(unittest.TestCase):

    def test_validation_issue_info(self):
        self.assertIn("INFORMATION", ValidationIssue.severity_string(ValidationIssue.INFORMATION))

    def test_validation_issue_warning(self):
        self.assertIn("WARNING", ValidationIssue.severity_string(ValidationIssue.WARNING))

    def test_validation_issue_error(self):
        self.assertIn("ERROR", ValidationIssue.severity_string(ValidationIssue.ERROR))

    def test_validation_issue_bad(self):
        with self.assertRaises(Exception):
            ValidationIssue.severity_string(-999)

    def test_validation_issue_string(self):
        s = str(ValidationIssue("MyObject", ValidationIssue.ERROR, "Some message", "this field"))
        s += ""
