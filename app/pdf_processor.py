# coding=utf-8


import logging
from os import listdir
from os import mkdir
from os import system
from os.path import basename
from os.path import join

from .utility import clear_dir
from .utility import walk_dir

from app.config import Config


class PDFProcessor:
    def __init__(self, conf):
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __pdf_to_image(self, pdf_path: str, dpi: str):
        out_dir = self.conf.out_dir
        dir_name = basename(pdf_path).split('.')[0]
        new_dir = join(out_dir, dir_name)
        try:
            mkdir(new_dir)
        except OSError as e:
            logging.error(e)
        if listdir(new_dir):
            logging.error('{0} is not empty'.format(new_dir))
            clear_dir(new_dir, file_ext=['.png'])
        system('gs -q -dSAFER -sDEVICE=pngmono -r{0} -dBATCH -dNOPAUSE -sOutputFile={1}%d.png {2}'
               .format(dpi, join(out_dir, dir_name) + '/', pdf_path))

        return True

    def __process_pdf_stack(self) -> bool:
        """
        Converts a pile of pdf files to images files.
        One image file per one pdf page is created and saved.
        File name is the pdf page no.
        """
        in_dir = self.conf.in_dir
        dpi = self.conf.pdf_dpi
        pdf_files = walk_dir(in_dir, file_type='pdf')

        if not pdf_files:
            return False

        for pdf_path in pdf_files:
            self.__pdf_to_image(pdf_path, dpi)

        return True

    def run(self):
        self.__process_pdf_stack()
