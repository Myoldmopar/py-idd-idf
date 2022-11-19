import logging

module_logger = logging.getLogger("eptransition.idd.processor")


class ValidationIssue:
    """
    This class stores information about any issue that occurred when reading an IDF file.

    :param str object_name: The object type that was being validated when this issue arose
    :param int severity: The severity of this issue, from the class constants
    :param str message: A descriptive message for this issue
    :param str field_name: The field name that was being validated when this issue arose, if available.
    """

    INFORMATION = 0
    WARNING = 1
    ERROR = 2

    def __init__(self, object_name, severity, message, field_name=None):
        self.object_name = object_name
        self.severity = severity
        self.message = message
        self.field_name = field_name

    @staticmethod
    def severity_string(severity_integer):
        """
        Returns a string version of the severity of this issue

        :param int severity_integer: One of the constants defined in this class (INFORMATION, etc.)
        :return: A string representation of the severity
        """
        if severity_integer == ValidationIssue.INFORMATION:
            return "INFORMATION"
        elif severity_integer == ValidationIssue.WARNING:
            return "*WARNING*"
        elif severity_integer == ValidationIssue.ERROR:
            return "**ERROR**"
        else:
            raise Exception("Bad integer passed into severity_string()")

    def __str__(self):
        msg = " * Issue Found; severity = " + ValidationIssue.severity_string(self.severity) + "\n"
        msg += "  Object Name = " + self.object_name + "\n"
        if self.field_name is not None:
            msg += "  Field Name = " + self.field_name + "\n"
        return msg


class IDFObject(object):
    """
    This class defines a single IDF object.  An IDF object is either a comma/semicolon delimited list of actual
    object data, or a block of line delimited comments.  Blocks of comment lines are treated as IDF objects so they can
    be intelligently written back out to a new IDF file after transition in the same location.

    Relevant members are listed here:

    :ivar str object_name: IDD Type, or name, of this object
    :ivar [str] fields: A list of strings, one per field, found for this object in the IDF file

    Constructor parameters:

    :param [str] tokens: A list of tokens defining this idf object, the first token in the list is the object type.
    :param bool comment_blob: A signal that this list is comment data, and not an actual IDF object; default is False.
                              indicating it is meaningful IDF data.
    """

    def __init__(self, tokens, comment_blob=False):
        self.comment = comment_blob
        if comment_blob:
            self.object_name = "COMMENT"
            self.fields = tokens
        else:
            self.object_name = tokens[0]
            self.fields = tokens[1:]

    def __str__(self) -> str:
        return f"{self.object_name} : {len(self.fields)} fields"

    def object_string(self, idd_object=None):
        """
        This function creates an intelligently formed IDF object.  If the current instance is comment data, it simply
        writes the comment block out, line delimited, otherwise it writes out proper IDF syntax.  If the matching IDD
        object is passed in as an argument, the field names are matched from that to create a properly commented
        IDF object.

        :param IDDObject idd_object: The IDDObject structure that matches this IDFObject
        :return: A string representation of the IDF object or comment block
        """
        s = ""
        if self.comment:
            for comment_line in self.fields:
                s += comment_line + "\n"
            return s
        if not idd_object:
            if len(self.fields) == 0:
                s = self.object_name + ";\n"
            else:
                s = self.object_name + ",\n"
                padding_size = 25
                for index, idf_field in enumerate(self.fields):
                    if index == len(self.fields) - 1:
                        terminator = ";"
                    else:
                        terminator = ","
                    s += "  " + (idf_field + terminator).ljust(
                        padding_size) + "!- \n"
            return s
        else:
            if len(self.fields) == 0:
                s = self.object_name + ";\n"
            elif '\\format' in idd_object.meta_data and 'singleLine' in idd_object.meta_data['\\format']:
                field_token_string = ",".join([field for field in self.fields])
                s = self.object_name + ',' + field_token_string + ';\n'
            else:
                idd_fields = idd_object.fields
                s = self.object_name + ",\n"
                padding_size = 25
                for index, idf_idd_fields in enumerate(zip(self.fields, idd_fields)):
                    idf_field, idd_field = idf_idd_fields
                    if index == len(self.fields) - 1:
                        terminator = ";"
                    else:
                        terminator = ","
                    if "\\units" in idd_field.meta_data:
                        units_string = " {" + idd_field.meta_data["\\units"][0] + "}"
                    else:
                        units_string = ""
                    if idd_field.field_name is None:  # pragma no cover  - our files don't have an object like this yet
                        idd_field.field_name = ""
                    s += "  " + (str(idf_field) + terminator).ljust(
                        padding_size) + "!- " + idd_field.field_name + units_string + "\n"
            return s

    def validate(self, idd_object):
        """
        This function validates the current IDF object instance against standard IDD field tags such as minimum and
        maximum, etc.

        :param IDDObject idd_object: The IDDObject structure that matches this IDFObject
        :return: A list of ValidationIssue instances, each describing an issue encountered
        """
        issues = []
        # first thing check if we even have an IDD object to validate against
        if idd_object is None:
            module_logger.debug("Got \"None\" for idd_object when validating {}".format(self.object_name))
            return issues
        # then check some object level things
        if isinstance(idd_object, str):
            # we have a single-line string-only idd object, just leave
            return issues
        if "\\min-fields" in idd_object.meta_data:
            minimum_required_fields = int(idd_object.meta_data["\\min-fields"][0])
            actual_num_fields = len(self.fields)
            for i in range(minimum_required_fields):
                if i < actual_num_fields:  # if the item is there
                    if not self.fields[i]:  # if it's blank
                        if "\\default" in idd_object.fields[i].meta_data:  # if it's blank but has a default value
                            self.fields[i] = idd_object.fields[i].meta_data["\\default"][0]  # fill with default
                            # if it doesn't have a default, just leave it blank, later checks will catch it
                else:  # if the item isn't even there
                    if "\\default" in idd_object.fields[i].meta_data:  # if it has a default value
                        self.fields.append(idd_object.fields[i].meta_data["\\default"][0])  # fill with default
                    else:  # or if it doesn't have a default
                        self.fields.append("")  # make sure it does have an entry (blank) and it will be caught later
                        issues.append(ValidationIssue(idd_object.name, ValidationIssue.WARNING,
                                                      "Field within \\min-fields missing and no default",
                                                      idd_object.fields[i].field_name))
        for idf, idd in zip(self.fields, idd_object.fields):
            if "\\required-field" in idd.meta_data:
                if idf == "":
                    issues.append(ValidationIssue(idd_object.name, ValidationIssue.WARNING,
                                                  "Blank required field found", idd.field_name))
                    continue
            an_code = idd.field_an_index
            if an_code[0] == "N":
                if idf.strip() != "":
                    try:
                        number = float(idf)
                        if "\\maximum" in idd.meta_data:
                            max_constraint_string = idd.meta_data["\\maximum"][0]
                            if max_constraint_string[0] == "<":
                                max_val = float(max_constraint_string[1:])
                                if number >= max_val:
                                    issues.append(ValidationIssue(
                                        idd_object.name, ValidationIssue.WARNING,
                                        "Field value higher than idd-specified maximum>; actual={}, max={}".format(
                                            number, max_val), idd.field_name))
                            else:
                                max_val = float(max_constraint_string)
                                if number > max_val:
                                    issues.append(ValidationIssue(
                                        idd_object.name, ValidationIssue.WARNING,
                                        "Field value higher than idd-specified maximum; actual={}, max={}".format(
                                            number, max_val), idd.field_name))
                        if "\\minimum" in idd.meta_data:
                            min_constraint_string = idd.meta_data["\\minimum"][0]
                            if min_constraint_string[0] == ">":
                                min_val = float(min_constraint_string[1:])
                                if number <= min_val:
                                    issues.append(ValidationIssue(
                                        idd_object.name, ValidationIssue.WARNING,
                                        "Field value lower than idd-specified minimum<; actual={}, max={}".format(
                                            number, max_val), idd.field_name))
                            else:
                                min_val = float(min_constraint_string)
                                if number < min_val:
                                    issues.append(ValidationIssue(
                                        idd_object.name, ValidationIssue.WARNING,
                                        "Field value lower than idd-specified minimum; actual={}, max={}".format(
                                            number, max_val), idd.field_name))
                    except ValueError:
                        if "\\autosizable" in idd.meta_data and idf.upper() == "AUTOSIZE":
                            pass  # everything is ok
                        elif "\\autocalculatable" in idd.meta_data and idf.upper() in ["AUTOCALCULATE", "AUTOSIZE"]:
                            pass  # everything is ok
                        elif idf.upper() == "AUTOSIZE":
                            issues.append(ValidationIssue(
                                idd_object.name, ValidationIssue.WARNING,
                                "Autosize detected in numeric field that is _not_ listed autosizable", idd.field_name))
                        elif idf.upper() == "AUTOCALCULATE":
                            issues.append(ValidationIssue(
                                idd_object.name, ValidationIssue.WARNING,
                                "Autocalculate detected in numeric field that is _not_ listed autocalculatable",
                                idd.field_name))
                        else:
                            issues.append(ValidationIssue(
                                idd_object.name, ValidationIssue.WARNING,
                                "Non-numeric value in idd-specified numeric field", idd.field_name))
        return issues

    def write_object(self, file_object):
        """
        This function simply writes out the idf string to a file object

        :param file_object: A file-type object that responds to a write command
        :return: None
        """
        file_object.write(self.object_string())
        return None


class IDFStructure(object):
    """
    An IDF structure representation.  This includes containing all the IDF objects in the file, as well as meta data
    such as the version ID for this IDD, and finally providing worker functions for accessing the IDD data

    Relevant "public" members are listed here:

    :ivar str file_path: The path given when instantiating this IDF, not necessarily an actual path
    :ivar float version_float: The floating point representation of the version of this IDD (for 8.6.0 it is 8.6)
    :ivar [IDFObject] objects: A list of all IDF objects found in the IDF

    Constructor parameters:

    :param str file_path: A file path for this IDF; not necessarily a valid path as it is never used, just available
                          for bookkeeping purposes.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.version_string = None
        self.version_float = None
        self.objects = None

    def get_idf_objects_by_type(self, type_to_get):
        """
        This function returns all objects of a given type found in this IDF structure instance

        :param str type_to_get: A case-insensitive object type to retrieve
        :return: A list of all objects of the given type
        """
        return [i for i in self.objects if i.object_name.upper() == type_to_get.upper()]

    def whole_idf_string(self, idd_structure=None):
        """
        This function returns a string representation of the entire IDF contents.  If the idd structure argument is
        passed in, it is passed along to object worker functions in order to generate an intelligent representation.

        :param IDDStructure idd_structure: An optional IDDStructure instance representing an entire IDD file
        :return: A string of the entire IDF contents, ready to write to a file
        """
        s = ""
        for idf_obj in self.objects:
            idd_obj = idd_structure.get_object_by_type(idf_obj.object_name)
            s += idf_obj.object_string(idd_obj) + "\n"
        return s

    def write_idf(self, idf_path, idd_structure=None):
        """
        This function writes the entire IDF contents to a file.  If the idd structure argument is
        passed in, it is passed along to object worker functions in order to generate an intelligent representation.

        :param str idf_path: The path to the file to write
        :param IDDStructure idd_structure: An optional IDDStructure instance representing an entire IDD file
        :return: None
        """
        with open(idf_path, "w") as f:
            f.write(self.whole_idf_string(idd_structure))
        return None

    def validate(self, idd_structure):
        """
        This function validates the current IDF structure instance against standard IDD object tags such as required
        and unique objects.

        :param idd_structure: An IDDStructure instance representing an entire IDD file
        :return: A list of ValidationIssue instances, each describing an issue encountered
        """
        issues = []
        required_objects = idd_structure.get_objects_with_meta_data("\\required-object")
        for r in required_objects:
            objects = self.get_idf_objects_by_type(r.name)
            if len(objects) == 0:
                issues.append(ValidationIssue(r.name, ValidationIssue.WARNING,
                                              message="Required object not found in IDF contents"))
        unique_objects = idd_structure.get_objects_with_meta_data("\\unique-object")
        for u in unique_objects:
            objects = self.get_idf_objects_by_type(u.name)
            if len(objects) > 1:
                issues.append(ValidationIssue(u.name, ValidationIssue.WARNING,
                                              message="Unique object has multiple instances in IDF contents"))
        for idf_object in self.objects:
            if idf_object.comment:
                continue
            idd_object = idd_structure.get_object_by_type(idf_object.object_name)
            this_object_issues = idf_object.validate(idd_object)
            if this_object_issues:
                issues.extend(this_object_issues)
        return issues

    def global_swap(self, dict_of_swaps):
        upper_case_swaps = {}
        for k, v in dict_of_swaps.items():
            upper_case_swaps[k.upper()] = v
        for idf_object in self.objects:
            if idf_object.comment:
                continue
            else:
                for i, idf_field in enumerate(idf_object.fields):
                    if idf_field.upper() in upper_case_swaps:
                        idf_object.fields[i] = upper_case_swaps[idf_field.upper()]
