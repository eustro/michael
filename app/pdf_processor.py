# coding=utf-8


import logging

from .util import clear_dir
from .util import walk_dir

from app.config import Config


class PDFProcessor:
    def __init__(self, conf):
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __pdf_to_image(self, pdf_path: str, dpi: str, image_type: str):
        from os import listdir
        from os import mkdir
        from os import system
        from os.path import basename
        from os.path import join

        out_dir = self.conf.out_dir
        dir_name = basename(pdf_path).split('.')[0]
        new_dir = join(out_dir, dir_name)
        try:
            mkdir(new_dir)
        except OSError:
            pass
        if listdir(new_dir):
            clear_dir(new_dir, file_ext=['.png', '.jpg', '.tif', '.tiff'])
        gs_command = 'gs'
        file_extension = image_type
        if file_extension == 'png':
            device = 'pngmono'
        elif file_extension in ('tif', 'tiff'):
            device = 'tiffgray'
        elif file_extension in ('jpg', 'jpeg'):
            device = 'jpeggray'
        else:
            device = 'pngmono'
        cmd = '{0} -q -dSAFER -sDEVICE={1} -r{2} -dBATCH -dNOPAUSE -sOutputFile={3}%d.{4} {5}'\
            .format(gs_command, device, dpi, join(out_dir, dir_name) + '/', file_extension, pdf_path)
        system(cmd)

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

        if self.conf.verbose:
            print("++ PDF Processor ++")
            print("   Processing " + str(len(pdf_files)) + " file(s) " + "in path " + in_dir)

        if not pdf_files:
            raise Exception('No PDF files found in: {0}'.format(in_dir))

        image_type = self.conf.image_type
        for pdf_path in pdf_files:
            if self.conf.verbose:
                print("    ... " + pdf_path + " ... ")
            self.__pdf_to_image(pdf_path, dpi, image_type)
        if self.conf.verbose:
            print("++++++++++++++++++++++")
        return True

    def run(self) -> None:
        try:
            self.__process_pdf_stack()
        except KeyboardInterrupt:
            print("\nComputation cancelled.")
