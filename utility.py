# *-- coding: utf-8 --*


"""
Module for basic operations on directories.
"""

from logging import error
from os import remove
from os import rmdir
from os import walk
from os.path import join


def walk_dir(path: str, file_type: str):
    """
    Walks directory to find all files with given file type extension.
    """
    try:
        __, __, filenames = next(walk(path), (None, None, []))
        file_paths = [join(path, a_file) for a_file in filenames
                      if a_file.endswith(file_type)]
        return file_paths
    except IOError as io:
        error(io)
        return None


def list_sub_dirs(path: str):
    """
    Lists all subdirectories in given directory.
    Retruns absolute paths of directories.
    """
    try:
        __, ls_dir, __ = next(walk(path), (None, None, []))
        ls_dir[:] = [join(path, entry) for entry in ls_dir]
        return ls_dir
    except IOError as io:
        error(io)
        return None


def clear_dir(path: str, del_sudirs=False, file_ext=['txt', 'png']):
    """
    Cleans recursively working directory of the application.
    Removes specified file types.
    Removes also all subdirectories if set to True.
    """
    for dirpath, subdirs, filenames in walk(path, topdown=False):
        file_paths = [join(dirpath, a_file) for a_file in filenames]
        for a_file in file_paths:
            if any(ext in a_file for ext in file_ext):
                try:
                    remove(a_file)
                except OSError as os:
                    error(os)
        if del_sudirs:
            dir_paths = [join(dirpath, sub) for sub in subdirs]
            for sub in dir_paths:
                rmdir(sub)
    return True


def open_file(path: str, mode='r', encoding='utf-8'):
    """
    Opens file in given mode and encoding (default UTF-8).
    Creates File, if it doesn't exist.
    Returns text string on sucess.
    Returns none on failure.
    """
    try:
        fp = open(path, mode)
        return fp
    except IOError as io:
        error(io)
        return None


def obj_to_json(obj, path: str) -> bool:
    """
    Exports a Python object ot json.
    Returns True on sucess.
    Returns False on Failure.
    """
    pass


def main():
    in_dir = '/Users/eugenstroh/Desktop/michael_the_syrian_1/'
    clear_dir(in_dir, del_sudirs=True)

if __name__ == '__main__':
    main()
