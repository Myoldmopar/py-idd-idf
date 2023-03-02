from io import StringIO
import logging
import os

from energyplus_iddidf import exceptions
from energyplus_iddidf.idf_objects import IDFObject, IDFStructure

module_logger = logging.getLogger("eptransition.idd.processor")


class IDFProcessor:
    """
    The core IDF Processor class.  Given an IDF via stream or path, this class has workers to robustly process the IDF
    into a rich IDFStructure instance.

    The constructor takes no arguments but sets up instance variables. Relevant "public" members are listed here:

    :ivar IDFStructure idf: The resulting IDFStructure instance after processing the IDF file/stream
    :ivar str file_path: A file path for this IDF, although it may be just a simple descriptor
    """

    def __init__(self):
        self.idf = None
        self.file_path = None
        self.input_file_stream = None

    def process_file_given_file_path(self, file_path):
        """
        This worker allows processing of an IDF file at a specific path on disk.

        :param file_path: The path to an IDF file on disk.
        :return: An IDFStructure instance created from processing the IDF file
        :raises ProcessingException: if the specified file does not exist
        """
        if not os.path.exists(file_path):
            raise exceptions.ProcessingException("Input file not found=\"" + file_path + "\"")
        self.input_file_stream = open(file_path, "r")
        self.file_path = file_path
        return self.process_file()

    def process_file_via_stream(self, idf_file_stream):
        """
        This worker allows processing of an IDF snippet via stream.  Most useful for unit testing, but possibly for
        other situations.

        :param file-like-object idf_file_stream: An IDF snippet that responds to typical file-like commands such as
                                                 read().  A common object would be the StringIO object.
        :return: An IDFStructure instance created from processing the IDF snippet
        """
        self.input_file_stream = idf_file_stream
        self.file_path = "/streamed/idf"
        return self.process_file()

    def process_file_via_string(self, idf_string):
        """
        This worker allows processing of an IDF snippet string.  Most useful for unit testing, but possibly for
        other situations.

        :param str idf_string: An IDF snippet string
        :return: An IDFStructure instance created from processing the IDF string
        """
        self.input_file_stream = StringIO(idf_string)
        self.file_path = "/string/idf/snippet"
        return self.process_file()

    def process_file(self):
        """
        Internal worker function that reads the IDF stream, whether it was constructed from a file path, stream or
        string.  This processor then processes the file line by line looking for IDF objects and comment blocks, and
        parsing them into a meaningful structure

        :return: An IDF structure describing the IDF contents
        :raises ProcessingException: for any issues encountered during the processing of the idf
        """
        self.idf = IDFStructure(self.file_path)
        # phase 0: read in lines of file
        lines = self.input_file_stream.readlines()

        class Blob:
            COMMENT = 1
            OBJECT = 2

            def __init__(self, blob_type, blob_lines=None):
                self.blob_type = blob_type
                if blob_lines is None:
                    blob_lines = []
                self.lines = blob_lines

        # should there maybe be 3 "state as of last line" options?
        # 1. reading comment block
        # 2. reading IDF block

        # so let's try keeping the idf in blobs of either comment data or object data
        current_blob = None
        initial_blobs = []
        for line in lines:
            line_text = line.strip()
            if len(line_text) == 0:
                continue
            elif line_text.startswith("!"):
                if current_blob is None:
                    current_blob = Blob(Blob.COMMENT)
                    current_blob.lines.append(line_text)
                elif current_blob.blob_type == Blob.COMMENT:
                    # just add to the lines and carry on
                    current_blob.lines.append(line_text)
                elif current_blob.blob_type == Blob.OBJECT:
                    # ignore it, we are still trying to read the object..
                    continue
            else:
                if current_blob is None:
                    # then this blob is fresh and is the start of a new object, but it could also be the end (one-liner)
                    current_blob = Blob(Blob.OBJECT)
                    actual_line = line_text
                    if "!" in line_text:
                        actual_line = line_text[:line_text.find("!")]
                    if ";" in actual_line:
                        # we end this object blob
                        current_blob.lines.append(line_text)
                        initial_blobs.append(current_blob)
                        current_blob = None
                    else:
                        current_blob.lines.append(line_text)
                elif current_blob.blob_type == Blob.OBJECT:
                    # then we should append this line to the current blob, but we also need to check if it is the end
                    current_blob.lines.append(line_text)
                    actual_line = line_text
                    if "!" in line_text:
                        actual_line = line_text[:line_text.find("!")]
                    if ";" in actual_line:
                        # we end this object blob
                        initial_blobs.append(current_blob)
                        current_blob = None
                elif current_blob.blob_type == Blob.COMMENT:
                    # then we need to package up the previous comment blob, and create this new one, but again..1-liner?
                    initial_blobs.append(current_blob)
                    current_blob = Blob(Blob.OBJECT)
                    current_blob.lines.append(line_text)
                    actual_line = line_text
                    if "!" in line_text:
                        actual_line = line_text[:line_text.find("!")]
                    if ";" in actual_line:
                        # we end this object blob
                        initial_blobs.append(current_blob)
                        current_blob = None
        if current_blob is not None:
            initial_blobs.append(current_blob)

        # next let's go blob by blob and clean up any trailing comments and such
        idf_objects = []
        for initial_blob in initial_blobs:
            if initial_blob.blob_type == Blob.COMMENT:
                idf_objects.append(IDFObject(initial_blob.lines, True))
            else:
                out_lines = []
                for line in initial_blob.lines:
                    line_text = line.strip()
                    this_line = ""
                    if len(line_text) > 0:
                        exclamation = line_text.find("!")
                        if exclamation == -1:
                            this_line = line_text
                        elif exclamation > 0:
                            this_line = line_text[:exclamation]
                        if not this_line == "":
                            out_lines.append(this_line.strip())
                # check these object lines for malformed idf syntax
                for li in out_lines:
                    if not (li.endswith(",") or li.endswith(";")):
                        raise exceptions.ProcessingException(
                            "IDF line doesn't end with comma/semicolon\nline:\"" + li + "\"")
                # intermediate: join entire array and re-split by semicolon
                idf_data_joined = "".join(out_lines)
                idf_object_strings = idf_data_joined.split(";")
                # phase 3: inspect each object and its fields
                for obj in idf_object_strings:
                    tokens = obj.split(",")
                    nice_object = [t.strip() for t in tokens]
                    if len(nice_object) == 1:
                        if nice_object[0] == "":
                            continue
                    idf_objects.append(IDFObject(nice_object))

        self.idf.objects = idf_objects

        try:
            self.idf.version_string = self.idf.get_idf_objects_by_type("Version")[0].fields[0]
            parse_version = True
        except IndexError:
            self.idf.version_string = 'UNKNOWN VERSION'
            parse_version = False
        if parse_version:
            try:
                version_tokens = self.idf.version_string.split(".")
                tmp_string = "{}.{}".format(version_tokens[0], version_tokens[1])
                self.idf.version_float = float(tmp_string)
            except ValueError:
                raise exceptions.ProcessingException(
                    "Found IDF version, but could not coerce into floating point representation")
        else:
            self.idf.version_float = 0.0
        return self.idf
