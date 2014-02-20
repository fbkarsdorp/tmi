import codecs
import os
from whoosh import index

from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.analysis import SimpleAnalyzer

from pattern.en import wordnet as WN

u = unicode

SCHEMA = Schema(motif = ID(stored=True),
                description = TEXT(analyzer=SimpleAnalyzer(), stored=True, phrase=True),
                wordnet = KEYWORD(stored=True, lowercase=True, scorable=True, commas=True))

if __name__ == '__main__':
    if not os.path.exists('index'):
        os.mkdir('index')
        ix = index.create_in('index', schema = SCHEMA, indexname="tmi")

    ix = index.open_dir('index', indexname='tmi')
    writer = ix.writer()
    for line in codecs.open('tmi.txt', encoding='utf-8'):
        line = line.strip().split('\t')
        if len(line) is not 3:
            continue
        motif, description, parse = line
        print motif
        keywords = set()
        for token in parse.split():
            word, pos, _, _, lemma = token.split('/')
            try:
                hypernyms = WN.synsets(lemma, 'NN')[0].hypernyms(recursive=True)
                keywords.update({w.senses[0] for w in hypernyms})
            except IndexError:
                pass
        writer.add_document(motif = u(motif), 
                            description = u(description), 
                            wordnet = u(', '.join(keywords)))
    writer.commit()

