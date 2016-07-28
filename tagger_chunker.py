# coding=utf-8


"""
Uses tree-tagger chunker, tagger and lemmatizer on text files.
"""

from logging import error
from treetaggerwrapper import TreeTagger
from treetaggerwrapper import make_tags
from pprint import pprint
from utility import list_sub_dirs
from utility import walk_dir
from utility import open_file
from utility import create_file
from utility import obj_to_json
from os.path import exists


def tag_file(path: str, lang: str):

    json_skeletton = []

    fp = open_file(path)
    if not fp:
        return None
    txt = fp.read()
    fp.close()
    tagger = TreeTagger(TAGLANG=lang)
    tags = tagger.tag_text(txt)
    tags = make_tags(tags)
    if not tags:
        return None
    for tag in tags:
        w = {'word': '', 'pos': '', 'lemma': ''}
        w['word'] = tag.word
        w['pos'] = tag.pos
        w['lemma'] = tag.lemma
        json_skeletton.append(w)

    try:
        return json_skeletton
    except TypeError as type_e:
        error(type_e)
        return None


def main():
    path = '/Users/eugenstroh/Desktop/michael_the_syrian_1/michael_1_4/1/1_political.txt'
    js_skeletton = tag_file(path, lang='fr')
    obj_to_json('/Users/eugenstroh/Desktop/michael_the_syrian_1/michael_1_4/1/', '1_political.json', js_skeletton)


if __name__ == '__main__':
    main()
