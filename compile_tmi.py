import codecs
import cPickle
import re

from pattern.en import parse, wordnet
from pattern.search import taxonomy, search, Classifier


# /////////////////////////////////////////////////////////////////////////////
# Functions to parse the motif index
# /////////////////////////////////////////////////////////////////////////////

def split_index_entry(entry):
    "Split entries in the TMI index (not motifs...)."
    return re.split('\.(?=[^-])', entry.strip(), maxsplit=1)

def add_motifs_from_index(index):
    motifs = {}
    for entry in index:
        motif = (number, description) = split_index_entry(entry)
        motifs[number] = (description, parse(description, lemmata=True))
    return motifs

def add_motifs(motifs, index):
    for motif in motifs:
        motif = (number, description) = motif.strip().split('\t')
        if number.endswith('.'): number = number[:-1]
        if number in index:
            continue
        index[number] = (description, parse(description, lemmata=True))
    return index

if __name__ == '__main__':
    with codecs.open('tmi-index.txt', encoding='utf-8') as inf:
        index = add_motifs_from_index(inf)
    with codecs.open('tmi-cleaned.txt', encoding='utf-8') as inf:
        index = add_motifs(inf, index)
    with open('tmi.txt', 'w') as out:
        for motif, (description, parse) in sorted(index.iteritems()):
            out.write('%s\t%s\t%s\n' % (motif.encode('utf-8'), description.encode('utf-8'), parse.encode('utf-8')))



