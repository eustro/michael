# *-- coding: utf-8 --*


"""
Module for basic operations on directories.
"""

from os import remove
from os import rmdir
from os import walk
from os.path import exists
from os.path import join


def walk_dir(path: str, file_type: str) -> list:
    """
    Walks directory to find all files with given file type extension.
    """
    try:
        __, __, file_names = next(walk(path), (None, None, []))
        file_paths = [join(path, a_file) for a_file in file_names
                      if a_file.endswith(file_type)]
        return sorted(file_paths, key=natural_keys)
    except Exception as e:
        raise Exception("Could not read {0}: {1}".format(path, repr(e)))


def list_sub_dirs(path: str) -> list:
    """
    Lists all subdirectories in given directory.
    Returns absolute paths of directories.
    """
    try:
        __, ls_dir, __ = next(walk(path), (None, None, []))
        ls_dir[:] = [join(path, entry) for entry in ls_dir]
        return sorted(ls_dir, key=natural_keys)
    except Exception as e:
        raise Exception("Could not read {0}: {1}".format(path, repr(e)))


def clear_dir(path: str, del_sudirs=False, file_ext=None) -> bool:
    """
    Cleans recursively working directory of the application.
    Removes specified file types.
    Removes also all subdirectories if set to True.
    """
    if not file_ext or not isinstance(file_ext, list):
        file_ext = []
    for dirpath, subdirs, filenames in walk(path, topdown=False):
        file_paths = [join(dirpath, a_file) for a_file in filenames]
        for a_file in file_paths:
            if any(ext in a_file for ext in file_ext):
                try:
                    remove(a_file)
                except Exception as e:
                    raise Exception("Could not read {0}: {1}".format(path, repr(e)))
        if del_sudirs:
            dir_paths = [join(dirpath, sub) for sub in subdirs]
            for sub in dir_paths:
                try:
                    rmdir(sub)
                except Exception as e:
                    raise Exception("Could not read {0}: {1}".format(path, repr(e)))
    return True


def open_file(path: str, encoding='utf-8'):
    """
    Opens file for reading only.
    Encoding may be specified (default: utf-8)
    Returns None, if file already exists.
    Returns file object on sucess.
    Returns None on failure.
    """
    if not exists(path):
        return None
    try:
        fp = open(path, mode='r', encoding=encoding)
        return fp
    except Exception as e:
        raise Exception("Could not read {0}: {1}".format(path, repr(e)))


def create_file(path: str, file_name: str, encoding='utf-8'):
    """
    Creates a new file for writing.
    Encoding may be specified (default: utf-8).
    Returns none, if file already exists.
    Returns file object on sucess.
    Returns None on failure.
    """
    file_path = join(path, file_name)
    if exists(file_path):
        fp = open_file(file_path)
        return fp
    try:
        fp = open(file_path, mode='x', encoding=encoding)
        return fp
    except Exception as e:
        raise Exception("Could not read {0}: {1}".format(path, repr(e)))


def dump_obj_to_json(out_path: str, file_name: str, obj: object) -> bool:
    """
    Dumps Python object to a json file.
    Returns True on sucess.
    Returns False on failure.
    """
    from json import dump
    if not exists(out_path):
        return False
    fp = create_file(out_path, file_name)
    if not fp:
        return False
    try:
        dump(obj, fp,
             ensure_ascii=False,
             separators=(', ', ': '),
             indent=4)
        fp.close()
        return True
    except Exception as e:
        raise Exception("Could not make json file: {0}".format(repr(e)))


def read_json_to_obj(file_path: str) -> bool:
    """
    Loads a Python object from a json file.
    Returns True on sucess.
    Returns False on failure.
    """
    from json import load
    if not exists(file_path):
        return False
    fp = open_file(file_path)
    if not fp:
        return False
    try:
        obj = load(fp)
        return obj
    except Exception as e:
        raise Exception("Could not make json file: {0}.".format(repr(e)))


def atoi(text: str) -> int or str:
    return int(text) if text.isdigit() else text


def natural_keys(text: str) -> list:
    import re
    return [atoi(c) for c in re.split('(\d+)', text)]

