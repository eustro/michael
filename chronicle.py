# coding=utf-8

"""
Arranges the four major text parts of the chronicle.
"""

from os.path import dirname
from os.path import basename
from os.path import exists
from os import rename
from logging import error
from skimage.io import imread
from utility import walk_dir
from utility import list_sub_dirs
from utility import open_file


def _set_params():
    params = {
        'width_ratio': 0.5,
        # DIN A4 PDF page.
        'length_res': 0,
        'width_res': 1,
        # Regular pages with 4 major parts.
        'parts_4': 4,
        'parts_5': 5,
        # Upper part
        'political': 1,
        # Left column
        'eccles': 2,
        # Right column
        'secular': 3,
        # Lower part
        'footnotes': 4
    }

    return params


def _arrange_text(in_dir: str, original_size: tuple) -> dict:
    """
    :param in_dir: Directory with single PDF-pages as PNG
    :param original_size: Original PDF-page as PNG
    :return: Dictionary with lists of correponding text fragments, where text
            text fragments are the absolute path of the cutted PNGs.
    """
    p = _set_params()

    text_boxes = walk_dir(in_dir, file_type='png')
    # Maybe no output by image processing, so need to be checked manually!
    if not text_boxes or text_boxes == []:
        return []

    images = []

    text_fragments = {'political': [],
                      'eccles': [],
                      'secular': [],
                      'footnotes': []}

    for box in text_boxes:
        im = imread(box, as_grey=True)
        if im is None:
            error('{0} not found'.format(box))
            continue
        images.append({'box': box, 'image': im})

    # If the layout is regular
    if len(text_boxes) == p['parts_4']:

        # Arrange footnotes
        text_fragments['footnotes'].append(images[3]['box'])

        # Arrange ecclesial part
        if images[2]['image'].shape[1] / original_size[1] >= 0.5:
            text_fragments['political'].append(images[2]['box'])
        else:
            text_fragments['eccles'].append(images[2]['box'])

        # Arrange secular part
        if images[1]['image'].shape[1] / original_size[1] >= 0.5:
            text_fragments['political'].append(images[1]['box'])
        else:
            text_fragments['secular'].append(images[1]['box'])

        # Arrange political part
        text_fragments['political'].append(images[0]['box'])

    # If there is one more part than necessary.
    # Probably one of those parts got cut one time more than necessary.
    elif len(text_boxes) == p['parts_5']:
        for im in reversed(images):
            if im['image'].shape[1] / original_size[1] >= 0.5 and not text_fragments['footnotes']:
                text_fragments['footnotes'].append(im['box'])
                continue
            if im['image'].shape[1] / original_size[1] < 0.5 and not text_fragments['secular']:
                text_fragments['secular'].append(im['box'])
                continue
            if im['image'].shape[1] / original_size[1] < 0.5 and not text_fragments['eccles']:
                text_fragments['eccles'].append(im['box'])
                continue
            else:
                text_fragments['political'].append(im['box'])
    # If number of parts is not regular, we have to do it manually.
    # Rename the path in '../[page_no]_unchecked' to find those cases.
    else:
        new_name = in_dir
        if in_dir.endswith('/'):
            new_name = in_dir[:-1]
        new_name += '_unchecked/'
        if '_unchecked/' not in in_dir:
            rename(in_dir, new_name)

    return text_fragments


def _rename_fragments(fragments: dict) -> bool:
    if not fragments:
        return False

    for frag, file_list in fragments.items():
        if not file_list:
            continue
        for file in file_list:
            file_parts = tuple(basename(str(file)).split('.'))
            file_name, file_ext = file_parts
            new_name = dirname(file) + '/' + file_name + '_' + str(frag) + '.' + file_ext
            if frag not in file:
                rename(file, new_name)

    return True


def _process_page(in_dir: str) -> bool:

    dirs = list_sub_dirs(in_dir)
    if not dirs:
        return False

    for sub_dir in dirs:
        original_page = walk_dir(dirname(sub_dir), file_type='png')
        if original_page:
            original_page = original_page[0]
        else:
            return False
        original_size = imread(original_page).shape
        fragments = _arrange_text(sub_dir, original_size)
        _rename_fragments(fragments)
    return True


def process_chronicle(in_dir: str) -> bool:
    dirs = list_sub_dirs(in_dir)
    if not dirs:
        return False

    for sub_dir in dirs:
        _process_page(sub_dir)
    return True


def main():
    in_dir = '/Users/eugenstroh/Desktop/michael_the_syrian_1/'
    process_chronicle(in_dir)


if __name__ == '__main__':
    main()
