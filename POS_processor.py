# coding=utf-8


"""
Uses tree-tagger chunker, tagger and lemmatizer on text files.
"""

from logging import error
import json
from utility import list_sub_dirs
from utility import walk_dir
from utility import open_file
from utility import obj_to_json

from config import Config


# TODO: Stanford NLP could also be implemented.
class NLPProcessor:
    def __init__(self, conf):
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

# TODO: Add config class
# TODO: Dump tags to json file to read later.
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
            error('{0} language not supported!'.format(lang))
            return []
        fp = open_file(path)
        if not fp:
            return []
        txt = fp.read()
        fp.close()
        tagger = TreeTagger(TAGLANG=lang)
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
            return json.loads(json_skeleton)
        except Exception as e:
            error(e)
            return []

    def __tag_file_stack(self):
        in_dir = self.conf.in_dir


    # TODO: Run function.
    def run(self):
        pass
