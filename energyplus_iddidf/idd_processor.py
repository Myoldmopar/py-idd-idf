from io import StringIO
import logging
import os
from typing import Optional

from energyplus_iddidf import exceptions
from energyplus_iddidf.idd_objects import IDDField, IDDObject, IDDStructure, IDDGroup

module_logger = logging.getLogger("eptransition.idd.processor")


class CurrentReadType:
    """
    Internal class containing constants for the different states of the actual IDD Processor engine
    """
    EncounteredComment_ReadToCR = 0
    ReadAnything = 1
    ReadingGroupDeclaration = 2
    ReadingObjectName = 3
    LookingForObjectMetaDataOrNextField = 4
    ReadingObjectMetaData = 5
    ReadingObjectMetaDataContents = 6
    ReadingFieldANValue = 7
    ReadingFieldMetaData = 8
    ReadingFieldMetaDataOrNextANValueOrNextObject = 9
    LookingForFieldMetaDataOrNextObject = 10
    LookingForFieldMetaDataOrNextField = 11


# keep a global dictionary of read IDD structures, could eventually move into the class, but right now we instantiate
# the class over and over so that wouldn't work
IDD_CACHE = {}


class IDDProcessor:
    """
    The core IDD Processor class.  Given an IDD via stream or path, this class has workers to robustly process the IDD
    into a rich IDDStructure instance.

    The constructor takes no arguments but sets up instance variables. Relevant "public" members are listed here:

    :ivar IDDStructure idd: The resulting IDDStructure instance after processing the IDD file/stream
    :ivar str file_path: A file path for this IDD, although it may be just a simple descriptor
    """

    def __init__(self):
        self.idd: Optional[IDDStructure] = None
        self.idd_file_stream = None
        self.file_path = None
        self.group_flag_string = "\\group"
        self.obj_flags = ["\\memo", "\\unique-object", "\\required-object", "\\min-fields",
                          "\\obsolete", "\\extensible", "\\format"]
        self.field_flags = ["\\field", "\\note", "\\required-field", "\\begin-extensible", "\\unitsBasedOnField",
                            "\\units", "\\ip-units", "\\scheduleunits", "\\minimum", "\\maximum", "\\default",
                            "\\deprecated", "\\autosizable", "\\autocalculatable", "\\type", "\\retaincase",
                            "\\key", "\\object-list", "\\reference-class-name", "\\reference", "\\external-list"]

    def process_file_given_file_path(self, file_path):
        """
        This worker allows processing of an IDD file at a specific path on disk.

        :param file_path: The path to an IDD file on disk.
        :return: An IDDStructure instance created from processing the IDD file
        :raises ProcessingException: if the specified file does not exist
        """
        if not os.path.exists(file_path):
            raise exceptions.ProcessingException("Input IDD file not found=\"" + file_path + "\"")  # pragma: no cover
        self.idd_file_stream = open(file_path, "rb")
        self.file_path = file_path
        return self.process_file()

    def process_file_via_stream(self, idd_file_stream):
        """
        This worker allows processing of an IDD snippet via stream.  Most useful for unit testing, but possibly for
        other situations.

        :param file-like-object idd_file_stream: An IDD snippet that responds to typical file-like commands such as
                                                 read().  A common object would be the StringIO object.
        :return: An IDDStructure instance created from processing the IDD snippet
        """
        self.idd_file_stream = idd_file_stream
        self.file_path = "/streamed/idd"
        return self.process_file()

    def process_file_via_string(self, idd_string):
        """
        This worker allows processing of an IDD snippet string.  Most useful for unit testing, but possibly for
        other situations.

        :param str idd_string: An IDD snippet string
        :return: An IDDStructure instance created from processing the IDD string
        """
        self.idd_file_stream = StringIO(idd_string)
        self.file_path = "/string/idd/snippet"
        return self.process_file()

    def peek_one_char(self) -> str:
        """
        Internal worker function that reads a single character from the internal IDD stream but resets the stream to
        the former position

        :return: A single character, the one immediately following the cursor, or None if it can't peek ahead.
        """
        pos = self.idd_file_stream.tell()
        c = self.idd_file_stream.read(1)
        if isinstance(c, bytes):
            try:
                c = c.decode('utf-8', errors='strict')
            except UnicodeDecodeError:
                c = '‍'  # this should really only occur if the idd is weirdly, I struggled creating a test for it
        elif isinstance(c, str):
            c = c
        # shouldn't be able to hit any other types... else: something
        if c == "":
            c = None
        self.idd_file_stream.seek(pos)
        return c

    def read_one_char(self) -> str:
        """
        Internal worker function that reads a single character from the internal IDD stream, advancing the cursor.

        :return: A single character, the one immediately following the cursor, or None if it can't read.
        """
        c = self.idd_file_stream.read(1)
        if isinstance(c, bytes):
            try:
                c = c.decode('utf-8', errors='strict')
            except UnicodeDecodeError:
                c = '‍'  # this should really only occur if the idd is weirdly, I struggled creating a test for it
        elif isinstance(c, str):
            c = c
        # shouldn't be able to hit any other types... else: something
        if c == "":
            c = None
        return c

    def process_file(self):
        """
        Internal worker function that reads the IDD stream, whether it was constructed from a file path, stream or
        string.  This state machine worker moves character by character reading tokens and processing them into
        a meaningful IDD structure.

        :return: An IDD structure describing the IDD contents
        :raises ProcessingException: for any erroneous conditions encountered during processing
        """
        # flags and miscellaneous variables
        line_index = 1  # 1-based counter for the current line of the file
        last_field_for_object = False  # this will be the last field if a semicolon is encountered
        magic_cache_key = None

        # variables used as we are building the input structure
        self.idd = IDDStructure(self.file_path)  # empty overall IDD structure
        cur_group = None  # temporary placeholder for an IDD group
        cur_object = None  # temporary placeholder for an IDD object
        cur_field = None  # temporary placeholder for an IDD field
        cur_obj_meta_data_type = None  # temporary placeholder for the type of object metadata encountered

        # variables related to building and processing tokens
        token_builder = ""

        # state machine variables
        read_status = CurrentReadType.ReadAnything  # current state machine reading status
        revert_status_after_comment = None  # reading status before the comment, shift back to this after comment's done

        # loop continuously, the loop will exit when it is done
        while True:

            # update the next character
            just_read_char = self.read_one_char()
            if not just_read_char:
                break

            # update the peeked character
            peeked_char = self.peek_one_char()
            if not peeked_char:
                peeked_char = "\n"  # to simulate that the line ended

            # if we are on Windows, we may end up with "\r", so move the read and peeked characters forward once
            if peeked_char == "\r":  # pragma no cover -- we don't unit test on Windows, so this won't be caught
                # in this case, we currently have like peeked_char='\r' and just_read_char='A'
                # we need to keep the just_read_char as it is, but move peeked char forward
                currently_just_read_char = just_read_char
                self.read_one_char()  # go ahead and digest the \r
                just_read_char = currently_just_read_char
                peeked_char = self.peek_one_char()
                if not peeked_char:
                    peeked_char = "\n"

            # jump if we are at an EOL
            if just_read_char == "\n":
                # increment the counter
                line_index += 1

            # if we aren't already processing a comment, and we have a comment:
            #  don't append to the token builder, just set read status
            if read_status != CurrentReadType.EncounteredComment_ReadToCR:
                if just_read_char == "!":
                    if read_status != CurrentReadType.ReadingFieldMetaData:
                        read_status = CurrentReadType.EncounteredComment_ReadToCR
                else:
                    token_builder += just_read_char

            # clear a preceding line feed character from the token
            if just_read_char == "\n" and len(token_builder) == 1:
                token_builder = ""

            if read_status == CurrentReadType.ReadAnything:

                # this is the most general case where we are wandering through the IDD looking for whatever
                # the possibilities are: comments, group declaration, or object definition
                if peeked_char == "\\":  # starting a group name
                    read_status = CurrentReadType.ReadingGroupDeclaration
                elif peeked_char in [" ", "\n", "\t"]:  # don't do anything
                    pass
                elif peeked_char == "!":
                    revert_status_after_comment = read_status
                    read_status = CurrentReadType.EncounteredComment_ReadToCR
                else:  # should be alphanumeric, just start reading object name
                    read_status = CurrentReadType.ReadingObjectName

            elif read_status == CurrentReadType.ReadingGroupDeclaration:

                # for the group declarations, we will just check to see if the
                # line has ended since it should be on a single line
                # if it hasn't then just keep on as is, if it has, parse the group name out of it
                if peeked_char == "\n":
                    # first update the previous group
                    if cur_group is not None:
                        self.idd.groups.append(cur_group)
                    group_declaration = token_builder.strip()
                    group_flag_index = group_declaration.find(self.group_flag_string)
                    if group_flag_index == -1:  # pragma: no cover
                        # add error to error report
                        raise exceptions.ProcessingException(
                            "Group keyword not found where expected",
                            line_index=line_index)
                    else:
                        group_declaration = group_declaration[len(self.group_flag_string):]
                    cur_group = IDDGroup(group_declaration.strip())
                    token_builder = ""
                    read_status = CurrentReadType.ReadAnything  # to start looking for groups/objects/comments/whatever

            elif read_status == CurrentReadType.ReadingObjectName:

                # the object names could have several aspects
                # they could be a single line object, such as: "Lead Input;"
                # they could be the title of a multi field object, such as: "Version,"
                # and they could of course have comments at the end
                # for now I will assume that the single line objects can't have metadata
                # so read until either a comma or semicolon, also trap for errors if we reach the end of line or comment
                if peeked_char == ",":
                    object_title = token_builder.strip()
                    cur_object = IDDObject(object_title)
                    token_builder = ""
                    self.read_one_char()  # to clear the comma
                    read_status = CurrentReadType.LookingForObjectMetaDataOrNextField
                elif peeked_char == ";":
                    # since this whole object is a single line, we can just add it directly to the current group
                    object_title = token_builder
                    # this is added to single-line objects because CurGroup isn't instantiated yet, should fix
                    self.idd.single_line_objects.append(object_title.strip())
                    token_builder = ""  # to clear the builder
                    self.read_one_char()  # to clear the semicolon
                    read_status = CurrentReadType.ReadAnything
                elif peeked_char in ["\n", "!"]:  # pragma: no cover
                    raise exceptions.ProcessingException(
                        "An object name was not properly terminated by a comma or semicolon",
                        line_index=line_index)

            elif read_status == CurrentReadType.LookingForObjectMetaDataOrNextField:

                token_builder = ""
                if peeked_char == "\\":
                    read_status = CurrentReadType.ReadingObjectMetaData
                elif peeked_char in ["A", "N"]:
                    read_status = CurrentReadType.ReadingFieldANValue
                elif peeked_char == "!":
                    revert_status_after_comment = read_status
                    read_status = CurrentReadType.EncounteredComment_ReadToCR
                elif peeked_char == " ":
                    # just let it keep reading
                    pass
                elif peeked_char == "\n":
                    # just let it keep reading
                    pass

            elif read_status == CurrentReadType.ReadingObjectMetaData:

                if peeked_char in [" ", ":", "\n"]:
                    if token_builder in self.obj_flags:
                        cur_obj_meta_data_type = token_builder
                        token_builder = ""
                        if cur_obj_meta_data_type in ["\\required-object", "\\unique-object"]:
                            # these do not carry further data, stop reading now
                            if cur_obj_meta_data_type not in cur_object.meta_data:
                                string_list = [None]
                                cur_object.meta_data[cur_obj_meta_data_type] = string_list
                            else:  # pragma: no cover   -- strings already exist, this is not valid...
                                raise exceptions.ProcessingException(
                                    "Erroneous object meta data - repeated \"" + token_builder + "\"",
                                    line_index=line_index,
                                    object_name=cur_object.name)
                            cur_obj_meta_data_type = None
                            read_status = CurrentReadType.LookingForObjectMetaDataOrNextField
                        else:
                            # these will have the following data, just set the flag
                            read_status = CurrentReadType.ReadingObjectMetaDataContents
                    else:  # pragma: no cover
                        # token_builder = ""
                        raise exceptions.ProcessingException(
                            "Erroneous object meta data tag found",
                            line_index=line_index,
                            object_name=cur_object.name)
                else:
                    # just keep reading
                    pass

            elif read_status == CurrentReadType.ReadingObjectMetaDataContents:

                if peeked_char == "\n":
                    data = token_builder.strip()
                    # quick validation of some meta data
                    if cur_obj_meta_data_type == "\\min-fields":
                        try:
                            float(data)
                        except ValueError:
                            raise exceptions.ProcessingException(
                                "Erroneous meta data for min-fields, non-numeric number of fields? Weird...",
                                line_index=line_index,
                                object_name=cur_object.name
                            )
                    if cur_obj_meta_data_type not in cur_object.meta_data:
                        string_list = [data]
                        cur_object.meta_data[cur_obj_meta_data_type] = string_list
                    else:
                        string_list = cur_object.meta_data[cur_obj_meta_data_type]
                        string_list.append(data)
                        cur_object.meta_data[cur_obj_meta_data_type] = string_list
                    token_builder = ""
                    cur_obj_meta_data_type = None
                    read_status = CurrentReadType.LookingForObjectMetaDataOrNextField

            elif read_status == CurrentReadType.ReadingFieldANValue:

                if peeked_char in [",", ";"]:
                    cur_field = IDDField(token_builder.strip())
                    token_builder = ""
                    if peeked_char == ",":
                        last_field_for_object = False
                    elif peeked_char == ";":
                        last_field_for_object = True
                    read_status = CurrentReadType.ReadingFieldMetaDataOrNextANValueOrNextObject
                elif peeked_char == "\n":  # pragma: no cover
                    raise exceptions.ProcessingException(
                        "Blank or erroneous ""AN"" field index value",
                        line_index=line_index,
                        object_name=cur_object.name)

            elif read_status == CurrentReadType.ReadingFieldMetaDataOrNextANValueOrNextObject:

                if peeked_char == "\\":
                    token_builder = ""
                    read_status = CurrentReadType.ReadingFieldMetaData
                elif peeked_char in ["A", "N"]:
                    token_builder = ""
                    # this is hit when we have an "AN" value right after a previous AN value, so no meta-data is added
                    if cur_field.field_name is None:
                        cur_field.field_name = ""
                    cur_object.fields.append(cur_field)
                    read_status = CurrentReadType.ReadingFieldANValue
                # If we hit a newline while searching here, we are moving onto the next object
                elif peeked_char == '\n':
                    token_builder = ""
                    # this is hit when we end an object when an "AN" declaration and nothing after it
                    if cur_field.field_name is None:
                        cur_field.field_name = ""
                    cur_object.fields.append(cur_field)
                    cur_group.objects.append(cur_object)
                    read_status = CurrentReadType.ReadAnything

            elif read_status == CurrentReadType.ReadingFieldMetaData:

                if peeked_char == "\n":

                    # for this one, let's read all the way to the end of the line, then parse data
                    flag_found = next((x for x in self.field_flags if x in token_builder), None)
                    if flag_found:
                        data = token_builder[len(flag_found):]
                        # data needs to start with a space, otherwise things like: \fieldd My Field would be valid
                        if len(data) > 0:
                            if data[0] not in [" ", ">", "<"]:
                                raise exceptions.ProcessingException(
                                    "Invalid meta data, expected a space after the meta data specifier before the data",
                                    line_index=line_index,
                                    object_name=cur_object.name,
                                    # field_name=cur_field.field_name
                                )
                        data = data.strip()
                        if flag_found == "\\field":
                            cur_field.field_name = data
                        else:
                            if flag_found not in cur_field.meta_data:
                                string_list = [data]
                                cur_field.meta_data[flag_found] = string_list
                            else:
                                string_list = cur_field.meta_data[flag_found]
                                string_list.append(data)
                                cur_field.meta_data[flag_found] = string_list
                    else:  # pragma: no cover
                        raise exceptions.ProcessingException(
                            "Erroneous field meta data entry found",
                            line_index=line_index,
                            object_name=cur_object.name,
                            # field_name=cur_field.field_name
                        )
                    token_builder = ""
                    if last_field_for_object:
                        read_status = CurrentReadType.LookingForFieldMetaDataOrNextObject
                    else:
                        read_status = CurrentReadType.LookingForFieldMetaDataOrNextField

                else:
                    # just keep reading
                    pass

            elif read_status == CurrentReadType.LookingForFieldMetaDataOrNextField:

                if peeked_char in ["A", "N"]:
                    token_builder = ""
                    cur_object.fields.append(cur_field)
                    read_status = CurrentReadType.ReadingFieldANValue
                elif peeked_char == "\\":
                    token_builder = ""
                    read_status = CurrentReadType.ReadingFieldMetaData
                elif peeked_char == "!":
                    revert_status_after_comment = read_status
                    read_status = CurrentReadType.EncounteredComment_ReadToCR
                elif peeked_char == "\n":
                    # just let it keep reading
                    pass

            elif read_status == CurrentReadType.LookingForFieldMetaDataOrNextObject:

                if peeked_char == "\\":
                    token_builder = ""
                    read_status = CurrentReadType.ReadingFieldMetaData

                elif peeked_char == "\n":
                    # blank line will mean we are concluding this object
                    token_builder = ""
                    cur_object.fields.append(cur_field)
                    cur_group.objects.append(cur_object)
                    read_status = CurrentReadType.ReadAnything

            elif read_status == CurrentReadType.EncounteredComment_ReadToCR:

                # set the flag for reading the next line if necessary
                token_builder += just_read_char
                if peeked_char == "\n":
                    if revert_status_after_comment is not None:
                        read_status = revert_status_after_comment
                        revert_status_after_comment = None
                    else:
                        read_status = CurrentReadType.ReadAnything
                    if "IDD_Version" in token_builder:
                        self.idd.version_string = token_builder.strip().split(" ")[1].strip()
                        try:
                            version_tokens = self.idd.version_string.split(".")
                            tmp_string = "{}.{}".format(version_tokens[0], version_tokens[1])
                            self.idd.version_float = float(tmp_string)
                        except ValueError:
                            raise exceptions.ProcessingException(
                                "Found IDD version, but could not coerce into floating point representation")
                    elif "IDD_BUILD" in token_builder:
                        self.idd.build_string = token_builder.strip().split(" ")[1].strip()
                        magic_cache_key = "{}__{}".format(self.idd.version_string, self.idd.build_string)
                        module_logger.debug("Encountered IDD_BUILD, checking cache for key {}".format(magic_cache_key))
                        if magic_cache_key in IDD_CACHE:
                            module_logger.debug("Found this IDD cache key in the cache, using existing entry")
                            self.idd = IDD_CACHE[magic_cache_key]
                            return self.idd
                    token_builder = ""

        # end the file here, but should watch for end-of-file in other CASEs also
        self.idd.groups.append(cur_group)

        # we should assert that we have version and build strings, even in testing
        if (not self.idd.version_float) or (not self.idd.build_string):
            raise exceptions.ProcessingException("IDD did not appear to include standard version headers")

        # save this idd structure in the cache
        if magic_cache_key:
            IDD_CACHE[magic_cache_key] = self.idd
            module_logger.debug("Storing this IDD in cache with key: {}".format(magic_cache_key))

        # and return the magically useful IDDStructure instance
        return self.idd
