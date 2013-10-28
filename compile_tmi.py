import codecs
import cPickle
import re

from pattern.en import parsetree, wordnet
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
        motifs[number] = (description, parsetree(description, lemmata=True))
    return motifs

def add_motifs(motifs, index):
    for motif in motifs:
        motif = (number, description) = motif.strip().split('\t')
        if number.endswith('.'): number = number[:-1]
        if number in index:
            continue
        index[number] = (description, parsetree(description, lemmata=True))
    return index

if __name__ == '__main__':
    with codecs.open('tmi-index.txt', encoding='utf-8') as inf:
        index = add_motifs_from_index(inf)
    with codecs.open('tmi-cleaned.txt', encoding='utf-8') as inf:
        index = add_motifs(inf, index)
    with open('tmi_parsed_flat.cPickle', 'w') as out:
        entries = []
        for i, motif in enumerate(sorted(index.iteritems())):
            cPickle.dump(motif, out)



