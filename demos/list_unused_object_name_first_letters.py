from pyiddidf.idd_processor import IDDProcessor

file_path = '/home/edwin/Projects/energyplus/repos/4eplus/idd/V8-9-0-Energy+.idd'

idd_processor = IDDProcessor().process_file_given_file_path(file_path)
object_names = []
first_letters = set()
for group in idd_processor.groups:
    for _object in group.objects:
        object_names.append(_object.name)
        first_letters.add(_object.name[0].upper())
found_letters_set = first_letters
full_alphabet_set = set([chr(i).upper() for i in range(ord('a'), ord('z') + 1)])
missing_letters = full_alphabet_set - found_letters_set
sorted(missing_letters)
print(missing_letters)
