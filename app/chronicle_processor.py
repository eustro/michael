# coding=utf-8

"""
Arranges the four major text parts of the chronicle.
"""

from os import rename
from os.path import basename
from os.path import dirname

from skimage.io import imread
from .util import list_sub_dirs
from .util import walk_dir


class ChronicleProcessor:
    def __init__(self, conf):
        from app.config import Config

        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __arrange_text(self, in_dir: str, original_size: tuple) -> dict:
        """
        :param in_dir: Directory with single document pages as images.
        :param original_size: Original resolution of the document.
        :return: Dictionary with lists of correponding text fragments, where text
                text fragments are the absolute path of the cutted PNGs.
        """
        page_width = original_size[1]
        image_type = self.conf.image_type
        images = walk_dir(in_dir, file_type=image_type)
        # Maybe no output by image processing, so need to be checked manually!
        if not images or images == []:
            raise Exception("No images found in {0}".format(in_dir))

        images = []

        text_fragments = {'political': [],
                          'secular': [],
                          'eccles': [],
                          'footnotes': []}

        for box in images:
            im = imread(box, as_grey=True)
            if im is None:
                print('{0} not found'.format(box))
                continue
            images.append({'box': box, 'image': im})
        # Two columns: Secular, ecclesial. Footnotes beneath.
        if len(images) == 3:
            # Label footnotes
            text_fragments['footnotes'].append(images[2]['box'])
            if images[1]['image'].shape[1] / page_width < 0.5:
                text_fragments['secular'].append(images[1]['box'])
            if images[0]['image'].shape[1] / page_width < 0.5:
                text_fragments['eccles'].append(images[0]['box'])
        # Political, secular, ecclesial
        if len(images) == 4:
            text_fragments['footnotes'].append(images[2]['box'])
            # Label footnotes
            text_fragments['footnotes'].append(images[3]['box'])

            # Arrange ecclesial part
            if images[2]['image'].shape[1] / page_width >= 0.5:
                text_fragments['political'].append(images[2]['box'])
            else:
                text_fragments['secular'].append(images[2]['box'])

            # Arrange secular part
            if images[1]['image'].shape[1] / page_width >= 0.5:
                text_fragments['political'].append(images[1]['box'])
            else:
                text_fragments['eccles'].append(images[1]['box'])

            # Arrange political part
            text_fragments['political'].append(images[0]['box'])
        # We can not be sure, with what column of the chronicle we are dealing with.
        # Case 1 part: There were probably more than one layout component merged together.
        # Case 2 parts: Probably one big column and footnotes, but we can't be sure which parts there are.
        #               Could be a L-formed shape of part that ended.
        # Case < 4 parts: Probably some layout components got fragmented.
        # Rename the path in '../[page_no]_unchecked' to find those cases.
        else:
            new_name = in_dir
            if in_dir.endswith('/'):
                new_name = in_dir[:-1]
            new_name += '_unchecked/'
            if '_unchecked/' not in in_dir:
                rename(in_dir, new_name)

        return text_fragments

    def _rename_fragments(self, fragments: dict) -> bool:
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

    def __process_page(self, in_dir) -> bool:
        file_type = self.conf.image_type
        dirs = list_sub_dirs(in_dir)
        if not dirs:
            return False

        for sub_dir in dirs:
            page = walk_dir(dirname(sub_dir), file_type=file_type)
            if page:
                page = page[0]
            else:
                return False
            original_size = imread(page).shape
            fragments = self.__arrange_text(sub_dir, original_size)
            self._rename_fragments(fragments)
        return True

    def __process_chronicle(self) -> bool:
        in_dir = self.conf.in_dir
        dirs = list_sub_dirs(in_dir)
        if not dirs:
            return False

        for sub_dir in dirs:
            self.__process_page(sub_dir)
        return True

    def run(self) -> None:
        try:
            self.__process_chronicle()
        except KeyboardInterrupt:
            print("\nComputation cancelled.")
