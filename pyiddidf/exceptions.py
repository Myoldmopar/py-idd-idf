class UnimplementedMethodException(Exception):
    """
    This exception occurs when a call is made to a function that should be implemented in a derived class
    but is not, so the base class function is called.  This is a developer issue.

    :param str class_name: The name of the base class where the virtual function is defined
    :param str method_name: The method name which should be overridden in the derived class
    """

    def __init__(self, class_name, method_name):
        self.class_name = class_name
        self.method_name = method_name

    def __str__(self):
        return "{} derived classes should override {}() method".format(self.class_name, self.method_name)


class FileAccessException(Exception):
    """
    This exception occurs when the transition tool encounters a problem accessing a prescribed input or output file.

    :param str file_path: The file path which is causing the issue
    :param str problem_type: The type of problem occurring, from the constants defined in this class
    :param str file_nickname: The nickname of the file, from the constants defined in this class
    :param str message: An optional additional message to write out
    """

    CANNOT_FIND_FILE = "cannot find file"
    CANNOT_READ_FILE = "cannot read file"
    CANNOT_WRITE_TO_FILE = "cannot write to file"
    FILE_EXISTS_MUST_DELETE = "file exists, must delete"
    TRIED_BUT_CANNOT_DELETE_FILE = "tried to delete file, but couldn't"

    ORIGINAL_INPUT_FILE = "original input file"
    UPDATED_INPUT_FILE = "updated input file"
    ORIGINAL_DICT_FILE = "original dictionary file"
    UPDATED_DICT_FILE = "updated dictionary file"

    def __init__(self, file_path, problem_type, file_nickname, message=None):
        self.file_path = file_path
        self.problem_type = problem_type
        self.file_nickname = file_nickname
        self.message = message

    def __str__(self):
        s = "File access problem occurred:\n  Trying to operate on *{}* at \"{}\"\n  Problem: {}".format(
            self.file_nickname, self.file_path, self.problem_type)
        if self.message:
            s += "  Message: " + self.message
        return s


class FileTypeException(Exception):
    """
    This exception occurs when the prescribed file types do not match the expected conditions.
    """

    ORIGINAL_INPUT_FILE = "original input file"
    UPDATED_INPUT_FILE = "updated input file"
    ORIGINAL_DICT_FILE = "original dictionary file"
    UPDATED_DICT_FILE = "updated dictionary file"

    def __init__(self, file_path, file_nickname, message):
        self.file_path = file_path
        self.file_nickname = file_nickname
        self.message = message

    def __str__(self):
        return "File type problem occurred:\n  Trying to operate on *{}* at \"{}\"\n  Problem: {}".format(
            self.file_nickname, self.file_path, self.message
        )


class ManagerProcessingException(Exception):
    """
    This exception occurs when the transition tool encounters an unexpected issue when doing the transition.
    """

    def __init__(self, msg, issues=None):
        self.message = msg
        self.issues = issues

    def __str__(self):
        msg = ""
        if self.issues:
            for i in self.issues:
                msg += str(i) + "\n"
        msg += self.message
        return msg


class ProcessingException(Exception):
    """
    This exception occurs when an unexpected error occurs during the processing of an input file.
    """

    def __init__(self, message, line_index=None, object_name="", field_name=""):
        super(ProcessingException, self).__init__(message)
        self.message = message
        self.line_index = line_index
        self.object_name = object_name

    def __str__(self):
        if self.line_index:
            return f"Processing Exception on line number {self.line_index}; message: {self.message} (tentative object" \
                   f" name: \"{self.object_name}\" "
        else:
            return f"Processing Exception; message: {self.message}"
