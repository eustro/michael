# *-- coding: utf-8 --*


"""
Module for basic operations on directories.
"""

from json import dump
from logging import error
from os import remove
from os import rmdir
from os import walk
from os.path import exists
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


def clear_dir(path: str, del_sudirs=False, file_ext=[]):
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
                try:
                    rmdir(sub)
                except OSError as os:
                    error(os)
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
    except IOError as io:
        error(io)
        return None


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
        fp = open(file_path, mode='w', encoding=encoding)
        return fp
    except IOError as io:
        error(io)
        return None


def obj_to_json(out_path: str, file_name: str, obj: object):
    """
    Dumps Python object to a json file.
    Returns True on sucess.
    Returns False on failure.
    """
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
        error(e)
        return False


def main():
    in_dir = '/Users/eugenstroh/Desktop/michael_the_syrian_1/'
    clear_dir(in_dir, del_sudirs=True)

if __name__ == '__main__':
    main()
