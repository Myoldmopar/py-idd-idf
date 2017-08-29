import unittest

from pyiddidf.exceptions import (
    UnimplementedMethodException,
    ManagerProcessingException,
    FileAccessException as eFAE,
    FileTypeException as eFTE,
    ProcessingException
)


class TestUnimplementedMethodException(unittest.TestCase):

    def setUp(self):
        self.e = UnimplementedMethodException("ClassName", "MethodName")

    def test_type(self):
        self.assertTrue(isinstance(self.e, Exception))

    def test_return_type(self):
        self.assertTrue(isinstance(self.e.__str__(), str))


class TestManagerException(unittest.TestCase):

    def setUp(self):
        self.e = ManagerProcessingException('mymessage', ['issue1', 'issue2'])

    def test_type(self):
        self.assertTrue(isinstance(self.e, Exception))

    def test_return_type(self):
        self.assertTrue(isinstance(self.e.__str__(), str))


class TestFileAccessException(unittest.TestCase):
    def setUp(self):
        self.e = eFAE("/file/path/", eFAE.CANNOT_FIND_FILE, eFAE.ORIGINAL_DICT_FILE, message="Heeey")

    def test_type(self):
        self.assertTrue(isinstance(self.e, Exception))

    def test_return_type(self):
        self.assertTrue(isinstance(self.e.__str__(), str))


class TestFileTypeException(unittest.TestCase):
    def setUp(self):
        self.e = eFTE("/file/path/fte/", eFTE.ORIGINAL_DICT_FILE, message="Whaaat?")

    def test_type(self):
        self.assertTrue(isinstance(self.e, Exception))

    def test_return_type(self):
        self.assertTrue(isinstance(self.e.__str__(), str))


class TestProcessingException(unittest.TestCase):
    def setUp(self):
        self.e = ProcessingException("mymessage", line_index=1, object_name="heyyo", field_name="myfield")

    def test_type(self):
        self.assertTrue(isinstance(self.e, Exception))

    def test_return_type(self):
        self.assertTrue(isinstance(self.e.__str__(), str))
