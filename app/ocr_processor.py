# coding=utf-8


"""
Module for tesseract ocr. Uses default system tesseract installation.
"""

import logging
import os

from .helpers import list_sub_dirs
from .helpers import walk_dir

from app.config import Config


class OCRProcessor:
    def __init__(self, conf):
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __ocr_on_image(self, image_path: str) -> bool:

        par = self.conf.params_ocr

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

    def __ocr_on_image_stack(self) -> bool:
        # Read Directories for processed PDF files
        in_dir = self.conf.in_dir
        pdf_dirs = list_sub_dirs(in_dir)
        if not pdf_dirs:
            return False
        # Read Directories of all pages in a PDF directory
        for one_page in pdf_dirs:
            pdf_pages = list_sub_dirs(one_page)
            for page in pdf_pages:
                for png in walk_dir(page, file_type='png'):
                    self.__ocr_on_image(png)
        return True

    def run(self):
        self.__ocr_on_image_stack()
