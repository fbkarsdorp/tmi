import codecs
import os

import ijson
from whoosh import index

from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.analysis import SimpleAnalyzer

from pattern.en import wordnet as WN

u = unicode

SCHEMA = Schema(motif = ID(stored=True, unique=True),
                description = TEXT(analyzer=SimpleAnalyzer(), 
                                   field_boost=2.0, stored=True, phrase=True),
                additional = TEXT(analyzer=SimpleAnalyzer(), 
                                  field_boost=1.5, stored=True, phrase=True),
                wn = KEYWORD(field_boost=1.0, stored=True, lowercase=True, scorable=True, commas=True),
                references = TEXT(analyzer=SimpleAnalyzer(), field_boost=0.5,
                                  stored=True, phrase=True))


if __name__ == '__main__':
    if not os.path.exists('index'):
        os.mkdir('index')
        ix = index.create_in('index', schema = SCHEMA, indexname="tmi")

    ix = index.open_dir('index', indexname='tmi')
    writer = ix.writer()
    with open("tmi.json") as infile:
        for item in ijson.items(infile, "item"):
            keywords = set()
            for lemma in item['lemmas']:
                try:
                    hypernyms = WN.synsets(lemma, 'NN')[0].hypernyms(recursive=True)
                    keywords.update({w.senses[0] for w in hypernyms})
                except IndexError:
                    pass
            writer.add_document(motif = u(item['motif']), 
                                description = u(item['description']),
                                additional = u(item['additional_description']), 
                                wn = u(', '.join(keywords)),
                                references=u(item['references']))
        writer.commit()

