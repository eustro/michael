# coding=utf-8


"""
Module for tesseract ocr. Uses default system tesseract installation.
"""

import os
import logging
from utility import list_sub_dirs
from utility import walk_dir


def _set_ocr_params(tess_dir='/opt/local/share',
                    lan='fra',
                    page_mode=3) -> dict:

    params = {'tess_dir': tess_dir,
              'lan': lan,
              'page_mode': page_mode}

    return params


def _ocr_on_image(image_path: str) -> bool:

    par = _set_ocr_params()

    if not os.path.exists(image_path):
        return False

    dir_name = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)[:-4]

    try:
        os.chdir(dir_name)
    except OSError as e:
        logging.error(e)
        return False

    os.system('tesseract --tessdata-dir {0} {1} {2} -l {3} -psm {4}'.format(par['tess_dir'],
                                                                            image_path,
                                                                            file_name,
                                                                            par['lan'],
                                                                            par['page_mode']))
    return True


def ocr_on_image_stack(in_dir: str) -> bool:
    # Read Directories for processed PDF files
    pdf_dirs = list_sub_dirs(in_dir)
    if not pdf_dirs:
        return False
    # Read Direcotries of all pages in a PDF directory
    for one_page in pdf_dirs:
        pdf_pages = list_sub_dirs(one_page)
        for page in pdf_pages:
            for png in walk_dir(page, file_type='png'):
                _ocr_on_image(png)
    return True


def main():
    in_dir = '/Users/eugenstroh/Desktop/michael_the_syrian_1/'

    ocr_on_image_stack(in_dir)

if __name__ == '__main__':
    main()
