from typing import List, Optional


class IDDField:
    """
    A simple class that defines a single field for an IDD object.  Relevant members are listed here:

    :ivar str field_an_index: Main identifier for this field
    :ivar dict(str,[str]) meta_data: A dictionary, where each key is a string metadata type, such as "\\note", and each
                                      value is a list of strings for each entry in the metadata of the key type.  So if
                                      the field has 3 note lines, the dictionary value for key "\\note" would be a 3
                                      element list, holding the 3 note lines.
    :ivar str field_name: A convenience variable holding the field name, if it is found in the metadata

    Constructor parameters:

    :param str an_index: The A_i or N_i descriptor for this field in the IDD, where i is an integer 1-...
    """

    def __init__(self, an_index: str):
        self.field_an_index = an_index
        self.meta_data = {}
        self.field_name: Optional[str] = None

    def __str__(self):
        return f"IDDField: {self.field_an_index} - {self.field_name}"


class IDDObject:
    """
    A simple class that defines a single IDD object.  Relevant members are listed here:

    :ivar str name: IDD Type, or name, of this object
    :ivar dict(str,[str]) meta_data: A dictionary, where each key is a string metadata type, such as "\\memo", and each
                                     value is a list of strings for each entry in the metadata of the key type.  So if
                                     the object has 3 memo lines, the dictionary value for key "\\memo" would be a 3
                                     element list, holding the 3 memo lines.
    :ivar list(IDDField) fields: A list of IDDField instances in order as read from the IDD

    Constructor parameters:

    :param str name: The object's type, or name
    """

    def __init__(self, name: str):
        self.name = name
        self.meta_data = {}
        self.fields: List[IDDField] = []

    def __str__(self):
        return f"IDDObject: {self.name} - {len(self.fields)} fields"


class IDDGroup:
    """
    A simple class that defines a single IDD group.  An IDD group is simply a container for IDD objects.
    Relevant members are listed here:

    :ivar str name: IDD Type, or name, of this group
    :ivar list(IDDObject) objects: A list of all objects found in the IDD within this group.

    Constructor parameters:

    :param str name: The group's name
    """

    def __init__(self, name: str):
        self.name = name
        self.objects: List[IDDObject] = []

    def __str__(self):
        return f"IDDGroup: {self.name} - {len(self.objects)} objects"


class IDDStructure:
    """
    An IDD structure representation.  This includes containing all the IDD objects (either inside groups or as
    standalone "single line objects"), as well as meta data such as the version ID for
    this IDD, and finally providing worker functions for accessing the IDD data

    Relevant "public" members are listed here:

    :ivar str file_path: The path given when instantiating this IDD, not necessarily an actual path
    :ivar float version_float: The floating point representation of the version of this IDD (for 8.6.0 it is 8.6)
    :ivar str build_string: The abbreviated git SHA used when generating this IDD
    :ivar [str] single_line_objects: A list of strings, each representing a raw, single-token, name-only IDD object
    :ivar list(IDDGroup) groups: A list of all groups found in the IDD, each of which will contain IDD objects

    Constructor parameters:

    :param str file_path: A file path for this IDD; not necessarily a valid path as it is never used, just available
                          for bookkeeping purposes.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.version_string: Optional[str] = None
        self.build_string: Optional[str] = None
        self.version_float: Optional[float] = None
        self.single_line_objects: List[str] = []
        self.groups: List[IDDGroup] = []

    def get_object_by_type(self, type_to_get):
        """
        Given a type name, this returns the IDD object instance, or a single string if it is a single-line object

        :param type_to_get: The name of the object to get, case-insensitive as it is compared insensitively inside
        :return: If the object is a single-line object, simply the name; if the object is a full IDDObject instance,
                 that instance is returned.  If a match is not found, this returns None.
        """
        # check the normal objects
        for g in self.groups:
            for o in g.objects:
                if o.name.upper() == type_to_get.upper():
                    return o
        # check single line objects? Weird...but might be useful
        for o in self.single_line_objects:
            if o.upper() == type_to_get.upper():
                return o
        # if we haven't returned, fail
        return None

    def get_objects_with_meta_data(self, meta_data):
        """
        Given an object-level metadata string (\\required-object, e.g.), this returns objects that contain that metadata

        :param meta_data: An object-level metadata string, such as \\required-object
        :return: A list of IDDObjects that contain this metadata
        """
        objects = []
        for g in self.groups:
            for o in g.objects:
                if meta_data in o.meta_data:
                    objects.append(o)
        return objects
        # not going to look at single line objects for this
