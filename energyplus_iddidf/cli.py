from argparse import ArgumentParser
from fnmatch import fnmatch
from json import dumps
from functools import reduce
from pathlib import Path
from sys import exit
from typing import Optional

from energyplus_iddidf.exceptions import ProcessingException
from energyplus_iddidf.idd_objects import IDDObject
from energyplus_iddidf.idd_processor import IDDProcessor


class Actions:
    IDDCheck = 'idd_check'
    FindIDDObjectsMatching = 'find_idd_objects_matching'
    SummarizeIDDObject = 'summarize_idd_object'


class ExitCodes:
    OK = 0
    ProcessingError = 1
    BadArguments = 2


# Eventually this could become a more feature rich CLI
def main_cli() -> int:
    parser = ArgumentParser(
        prog="energyplus_idd_idf",
        description="EnergyPlus IDD/IDF Utility Command Line",
        epilog="This CLI is in infancy and will probably have features added over time"
    )
    parser.add_argument('filename', help="Path to IDD/IDF file to be operated upon")  # positional argument
    parser.add_argument(
        '--idd_check', action='store_const', const=Actions.IDDCheck,
        help="Process the given IDD file and report statistics and issues"
    )
    parser.add_argument(
        '--idd_obj_matches', type=str, help="Find IDD objects that match the given basic pattern"
    )
    parser.add_argument(
        '--summarize_idd_object', type=str, help="Print a summary of a single IDD object by name"
    )
    args = parser.parse_args()
    all_options = [
        args.idd_check, args.idd_obj_matches, args.summarize_idd_object
    ]
    if all([x is None for x in all_options]):
        print(dumps({'message': "Nothing to do...use command line switches to perform operations"}, indent=2))
        return ExitCodes.OK
    p = Path(args.filename)
    if not p.exists():
        print(dumps({'message': "Supplied file does not appear to exist, check paths and retry!"}, indent=2))
        return ExitCodes.BadArguments
    # for now assume it's always the IDD, so we don't have to repeat this code
    processor = IDDProcessor()
    try:
        processor.process_file_given_file_path(str(p))
    except ProcessingException:
        print("Issues occurred during processing")
        return ExitCodes.ProcessingError
    if args.idd_check:
        num_groups = len(processor.idd.groups)
        num_objects = reduce(
            lambda x, y: x + y,
            [len(g.objects) for g in processor.idd.groups],
            0
        )
        print(dumps({
            'message': 'Everything looks OK',
            'content': {
                'idd_version': processor.idd.version_string,
                'idd_build_id': processor.idd.build_string,
                'num_groups': num_groups,
                'num_objects': num_objects
            }
        }, indent=2))
    elif args.idd_obj_matches:
        pattern = args.idd_obj_matches
        matching_objects = []
        for g in processor.idd.groups:
            for o in g.objects:
                obj_name = o.name
                if fnmatch(obj_name, pattern):
                    matching_objects.append(o)
        print(dumps({
            'message': 'Everything looks OK',
            'content': {
                'pattern': pattern,
                'matching_objects': [
                    o.name for o in matching_objects
                ]
            }
        }, indent=2))
    elif args.summarize_idd_object:
        object_name = args.summarize_idd_object.upper()
        matching_object: Optional[IDDObject] = None
        for g in processor.idd.groups:
            for o in g.objects:
                obj_name = o.name.upper()
                if fnmatch(obj_name, object_name):
                    matching_object = o
        if matching_object is None:
            print(dumps({'message': f"Could not find matching object by name {object_name}"}, indent=2))
            return ExitCodes.BadArguments
        print(dumps({
            'message': 'Everything looks OK',
            'content': {
                'searched_object_name': object_name,
                'field': [
                    f"{f.field_an_index} : {f.field_name}" for f in matching_object.fields
                ]
            }
        }, indent=2))
    return ExitCodes.OK


if __name__ == "__main__":  # pragma: no cover
    exit(main_cli())
