# coding=utf-8


"""
Uses tree-tagger chunker, tagger and lemmatizer on text files.
"""

import os
from logging import error

from .helpers import open_file
from .helpers import list_sub_dirs
from .helpers import walk_dir
from .helpers import dump_obj_to_json

from app.config import Config


# TODO: Change triple loop, use a recursive search through path.
# TODO: Stanford NLP could also be implemented.
class POSProcessor:
    def __init__(self, conf):
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __tag_file_tree_tagger(self, path: str, lang: str) -> list:
        """
        @path: path of file.
        @lang: language to be used for tagging.
        Chunking and tagging of a file using the TreeTagger.
        Returns a json-skeleton on success. Skeleton can be used to create
        a json file and to reload tagging results.
        Returns None on Failure.
        """
        from treetaggerwrapper import TreeTagger
        from treetaggerwrapper import make_tags

        json_skeleton = []
        if lang not in ('en', 'es', 'de', 'fr'):
            error('{0} language not supported by TreeTagger!'.format(lang))
            return []
        fp = open_file(path)
        if not fp:
            return []
        try:
            txt = fp.read()
            fp.close()
        except Exception as e:
            error(e)
            return []
        # TODO: Find a way to include treetagger location.
        tagger = TreeTagger(TAGLANG=lang, TAGDIR='/Users/eugenstroh/TreeTagger')
        tags = tagger.tag_text(txt)
        tags = make_tags(tags)
        if not tags:
            return []
        for tag in tags:
            w = {'word': tag.word,
                 'pos': tag.pos,
                 'lemma': tag.lemma}
            json_skeleton.append(w)

        try:
            return json_skeleton
        except Exception as e:
            error(e)
            return []

    def __tag_file_stanford_tagger(self, path: str, lang: str) -> list:
        pass

    def __tag_file_stack(self):
        in_dir = self.conf.in_dir
        all_pdf_files = list_sub_dirs(in_dir)
        for pdf_file in all_pdf_files:
            pdf_pages = list_sub_dirs(pdf_file)
            for page in pdf_pages:
                txt_files = walk_dir(page, file_type='txt')
                for txt in txt_files:
                    fname = os.path.basename(txt)
                    # Overwrite file, if exists.
                    if 'pos' in fname:
                        # Truncate _pos.txt
                        fname = fname[:-8]
                    else:
                        # Truncate .txt
                        fname = fname[:-4]
                    json_obj = self.__tag_file_tree_tagger(txt, self.conf.lang)
                    dump_obj_to_json(page, fname + '_pos' + '.txt', json_obj)

    # TODO: Run function.
    def run(self) -> None:
        self.__tag_file_stack()
