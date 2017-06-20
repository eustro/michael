# coding=utf-8


"""
Uses tree-tagger chunker, tagger and lemmatizer on text files.
"""

import os


class POSProcessor:
    def __init__(self, conf):
        from app.config import Config
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __tag_file_tree_tagger(self, path: str, lang: str, tree_tagger_dir: str) -> list:
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

        from .util import open_file

        json_skeleton = []
        if lang not in ('en', 'es', 'de', 'fr'):
            raise Exception('{0} language not supported by TreeTagger!'.format(lang))
        fp = open_file(path)
        if not fp:
            return []
        try:
            txt = fp.read()
            fp.close()
        except Exception as e:
            raise Exception("Could not read txt file: {0}, {1}".format(path, repr(e)))

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
            raise Exception("Could not parse json: {0}".format(repr(e)))

    def __tag_file_stanford_tagger(self, path: str, lang: str) -> list:
        pass

    # TODO: Change triple loop, use a recursive search through path.
    def __tag_file_stack(self):
        from .util import list_sub_dirs
        from .util import walk_dir
        from .util import dump_obj_to_json

        in_dir = self.conf.in_dir
        all_docs = list_sub_dirs(in_dir)
        for doc in all_docs:
            doc_page = list_sub_dirs(doc)
            for page in doc_page:
                txt_files = walk_dir(page, file_type='txt')
                for txt in txt_files:
                    fname = os.path.basename(txt)
                    # Overwrite file, if exists.
                    if 'pos' in fname:
                        # Truncate _pos.txt
                        fname = fname[:-8]
                    else:
                        # Truncate .txt
                        fname = str(fname.split('.')[0])
                    json_obj = self.__tag_file_tree_tagger(txt, self.conf.lang, tree_tagger_dir='')
                    dump_obj_to_json(page, fname + '_pos' + '.json', json_obj)

    def run(self) -> None:
        self.__tag_file_stack()
