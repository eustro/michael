# coding=utf-8


"""
Module provides optical text box recognition in image files.
"""

from os import mkdir
from os import system
from os.path import join
from os.path import basename
from os.path import exists
from os.path import dirname
from os.path import realpath
from os import listdir
from json import json
import logging
import warnings
import numpy as np
from skimage import io
from skimage.transform import rotate
from utility import walk_dir
from utility import list_sub_dirs
from utility import clear_dir


cwd = dirname(realpath(__file__))


def _set_params(resolution: tuple) -> dict:
    if resolution:
        dim_1, dim_2 = resolution
    # Reference resolution of 150 dpi.
    # Resolution lower than that yields inaccurate results.
    def_dim_1, def_dim_2 = 1200, 1600

    # Works for res around 1200 x 1600pixels (150 dpi).
    params = {'black_value': 0.1,
              'white_value': 0.9,

              'min_black_pixels': 0.00625 * min(dim_1, dim_2) + 5,
              'min_white_pixels': min(dim_1, dim_2),
              'min_white_lines': 0.006,
              'min_black_lines': 0.001875,
              'min_crop_ratio': 9.0,

              'correction_upper': -10,
              'correction_lower': -5,
              'correction_left': -15,
              'correction_right': +15,

              'vertical_margin': int(0.01 * float(dim_2)),
              'horizontal_margin': int(0.01 * float(dim_1))}

    params['min_white_lines'] *= max(dim_1, dim_2)

    params['min_black_lines'] *= max(dim_1, dim_2)

    if params['horizontal_margin'] > 0:
        params['min_white_pixels'] -= 2 * params['horizontal_margin']

    if dim_1 + dim_2 > def_dim_1 + def_dim_2:
        ratio = float(dim_1 + dim_2) / float(def_dim_1 + def_dim_2)
        params['correction_upper'] *= ratio
        params['correction_lower'] *= ratio
        params['correction_left'] *= ratio
        params['correction_right'] *= ratio

    return params


def _detect_text_boxes(image: np.ndarray, horizontal=False) -> list:
    if image.ndim > 2 or 0 in image.shape:
        return []

    params = _set_params(image.shape)

    dim1, dim2 = image.shape

    if horizontal and max(dim1, dim2) / min(dim1, dim2) > params['min_crop_ratio']:
        return []

    if horizontal:
        image_copy = rotate(image, 90, resize=True)
    else:
        image_copy = image

    state_in = False
    state_out = True

    curr_white_lines = 0

    cut_positions = []

    for row in range(params['vertical_margin'],
                     image_copy.shape[0] - params['vertical_margin']):

        black_pixel = 0
        white_pixel = 0

        for col in range(params['horizontal_margin'],
                         image_copy.shape[1] - params['horizontal_margin']):

            if state_in:

                if image_copy[row, col] >= params['white_value']:
                    white_pixel += 1

                if white_pixel >= params['min_white_pixels']:
                    curr_white_lines += 1

                if image_copy[row, col] <= params['black_value']:
                    black_pixel += 1

                if black_pixel >= params['min_black_pixels']:
                    curr_white_lines = 0

                if curr_white_lines >= params['min_white_lines']:
                    curr_white_lines = 0
                    state_out = True
                    state_in = False
                    entry_p = cut_positions[-1][0]
                    exit_p = row
                    if horizontal:
                        cut_positions[-1] = (entry_p + params['correction_left'],
                                             exit_p + params['correction_right'])
                    else:
                        cut_positions[-1] = (entry_p + params['correction_upper'],
                                             exit_p + params['correction_lower'])
                    break

            elif state_out:

                if image_copy[row, col] <= params['black_value']:
                    black_pixel += 1

                if black_pixel >= params['min_black_pixels']:
                    state_in = True
                    state_out = False
                    entry_point = row
                    cut_positions.append((entry_point, None))
                    break

    cut_positions[:] = [pos for pos in cut_positions if None not in pos]

    return cut_positions


def _get_minimum_text_box(image: np.ndarray):
    # TODO
    pass


def _get_text_from_image(image: np.ndarray) -> list:
    params = {'filter_small_hor': 0.035,
              'filter_small_ver': 0.15,
              'max_no_of_hor_cuts': 10,
              'max_no_of_ver_cuts': 2}

    text_images = []

    hor_cuts = _detect_text_boxes(image)

    if not hor_cuts:
        return image

    if len(hor_cuts) > params['max_no_of_hor_cuts']:
        return image

    for hor_cut in hor_cuts:

        x_in, x_out = hor_cut

        x_in = int(x_in)
        x_out = int(x_out)

        if abs(x_out - x_in) < image.shape[0] * params['filter_small_hor']:
            continue

        hor_image = image[x_in:x_out][:]
        ver_cuts = _detect_text_boxes(hor_image, horizontal=True)

        if not ver_cuts:
            text_images.append(hor_image)

        if len(ver_cuts) > params['max_no_of_ver_cuts']:
            text_images.append(hor_image)
            continue

        for ver_cut in ver_cuts:

            y_in, y_out = ver_cut

            y_in = int(y_in)
            y_out = int(y_out)

            if abs(y_out - y_in) < image.shape[1] * params['filter_small_ver']:
                text_images.append(hor_image)
                continue

            ver_image = hor_image[:, hor_image.shape[1] - y_out:hor_image.shape[1] - y_in]

            text_images.append(ver_image)

    return text_images


def _save_text_box(image: np.ndarray, out_dir: str, file_name: str) -> bool:
    # If not enough axes or empty slice, break.
    if image.ndim < 2 or 0 in image.shape:
        return False
    if not exists(out_dir):
        return False
    if not out_dir.endswith('/'):
        out_dir += '/'
    path = join(out_dir, file_name)
    try:
        io.imsave(path, image)
        return True
    except IOError as e:
        logging.error(e)
        return False


def _process_image(image: np.ndarray, out_dir: str, page_no: str, file_type='png') -> bool:
    path = join(out_dir, page_no)

    if exists(path) and walk_dir(path, file_type='png'):
        return True

    try:
        mkdir(join(out_dir, page_no))
    except OSError as e:
        logging.error(e)
        return False

    file_name = 1

    for text_image in _get_text_from_image(image):
        fname = str(file_name) + '.' + file_type
        _save_text_box(text_image, path, fname)
        file_name += 1

    return True


def process_image_stack(in_dir: str, image_type='png') -> bool:
    """
    process_image_stack(in_dir, out_dir) -> Bool.

    Get all image files in the subdirectories of in_dir and get all text boxes.
    Save each of the text boxes as png in a separate file in a subdirectory.



    Constructs a structure of a pdf pag like following:
        page1.png
        page1:
            text_box_1
            text_box_2
            ...
        page2.png
        page2:
            text_box_1
            ...
        page3.png
        page3:
            ...

    Return True on success or False on failure or in case of empty input.
    """
    dirs = list_sub_dirs(in_dir)

    if not dirs:
        return False

    for d in dirs:
        image_files = walk_dir(d, image_type)
        if not image_files:
            return False

        for image_path in image_files:
            image = io.imread(image_path, as_grey=True)
            _process_image(image, d, basename(image_path)[:-4])

    return True


def _pdf_to_image(pdf_path: str, out_dir: str, dpi: str):
    dir_name = basename(pdf_path).split('.')[0]
    new_dir = join(out_dir, dir_name)
    try:
        mkdir(new_dir)
    except OSError as e:
        logging.error(e)
    if listdir(new_dir):
        logging.error('{0} is not empty'.format(new_dir))
        clear_dir(new_dir)
    system('gs -q -dSAFER -sDEVICE=pngmono -r{0} -dBATCH -dNOPAUSE -sOutputFile={1}%d.png {2}'
           .format(dpi, join(out_dir, dir_name) + '/', pdf_path))

    return True


def process_pdf_stack(in_dir: str, out_dir: str, dpi='300') -> bool:
    """
    Converts a pile of pdf files to images files.
    One image file per one pdf page is created and saved.
    File name is the pdf page no.
    """
    pdf_files = walk_dir(in_dir, file_type='pdf')

    if not pdf_files:
        return False

    for pdf_path in pdf_files:
        _pdf_to_image(pdf_path, out_dir, dpi)

    return True


def main():
    """Simple test."""
    warnings.simplefilter('default', UserWarning)
    in_dir = '/Users/eugenstroh/Desktop/michael_the_syrian_1/'
    out_dir = '/Users/eugenstroh/Desktop/michael_the_syrian_1/'

    process_pdf_stack(in_dir, out_dir)

    process_image_stack(in_dir)

    # clear_dir(in_dir)


if __name__ == '__main__':
    main()
