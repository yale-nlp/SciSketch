import json

def write_object_to_file(obj, file_name):
    """
    write object to file
    """
    with open(file_name, "w") as f:
        json.dump(obj, f, indent=2)

def write_string_to_file(string, file_name):
    """
    write string to file
    """
    with open(file_name, "w") as f:
        f.write(string)