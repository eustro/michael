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
        layout_components = walk_dir(in_dir, file_type=image_type)
        # Maybe no output by image processing, so need to be checked manually!
        if not layout_components or layout_components == []:
            raise Exception("No images found in {0}".format(in_dir))

        images = []

        text_fragments = {'political': [],
                          'misc': [],
                          'eccles': [],
                          'footnotes': []}

        for component in layout_components:
            im = imread(component, as_grey=True)
            if im is None:
                print('{0} not found'.format(component))
                continue
            images.append({'component': component, 'image': im})
        for i, im in enumerate(images):
            image_width = im['image'].shape[1]
            if image_width / page_width >= 0.5\
                    and not (text_fragments['misc'] or text_fragments['eccles'])\
                    and i < len(images) - 1:
                text_fragments['political'].append(im['component'])
                continue
            if (image_width / page_width < 0.5) and not text_fragments['misc']:
                text_fragments['misc'].append(im['component'])
                continue
            if (image_width / page_width < 0.5) and not text_fragments['eccles']:
                text_fragments['eccles'].append(im['component'])
                continue
            if (image_width / page_width >= 0.5) and i >= len(images) - 2:
                text_fragments['footnotes'].append(im['component'])
                continue
        if not text_fragments:
            new_name = in_dir
            if in_dir.endswith('/'):
                new_name = in_dir[:-1]
            new_name += '_unchecked/'
            if '_unchecked' not in in_dir:
                rename(in_dir, new_name)

        return text_fragments

    def _rename_fragments(self, fragments: dict):
        if not fragments:
            raise Exception('Fragments empty: {0}'.format(fragments))

        for frag, file_list in fragments.items():
            if not file_list:
                continue
            for file in file_list:
                file_parts = tuple(basename(str(file)).split('.'))
                file_name, file_ext = file_parts
                new_name = dirname(file) + '/' + file_name + '_' + str(frag) + '.' + file_ext
                if frag not in file:
                    try:
                        rename(file, new_name)
                    except:
                        raise Exception("Could not rename layout component {0} to new name: {1}".format(file, new_name))

    def __process_page(self, in_dir) -> bool:
        file_type = self.conf.image_type
        dirs = list_sub_dirs(in_dir)
        if not dirs:
            raise Exception('Directory structure does not seem to be correct.')
        for sub_dir in dirs:
            pages = walk_dir(dirname(sub_dir), file_type=file_type)
            if pages:
                pages = pages[0]
            else:
                raise Exception('Could not find corresponding original page for {0}'.format(sub_dir))
            original_size = imread(pages).shape
            fragments = self.__arrange_text(sub_dir, original_size)
            self._rename_fragments(fragments)
        return True

    def __process_chronicle(self) -> bool:
        in_dir = self.conf.in_dir
        dirs = list_sub_dirs(in_dir)
        if self.conf.verbose:
            print("++ Chronicle Processor ++")
            print("   Processing file(s) in path " + in_dir)
        if not dirs:
            raise Exception('Directory structure does not seem to be correct: {0}'.format(in_dir))

        for sub_dir in dirs:
            if self.conf.verbose:
                print("    ... " + sub_dir + " ... ")
            self.__process_page(sub_dir)

        if self.conf.verbose:
            print("++++++++++++++++++++++")

        return True

    def run(self) -> None:
        try:
            self.__process_chronicle()
        except KeyboardInterrupt:
            print("\nComputation cancelled.")
