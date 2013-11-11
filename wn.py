#! /usr/bin/python

import sys
from pattern.search import taxonomy
from pattern.search import WordNetClassifier

taxonomy.classifiers.append(WordNetClassifier())

if __name__ == '__main__':
	word = sys.argv[1].strip()
	print 'PARENTS:\n', ''.join('%s(%s) %s\n' % (' '*i, i, parent) for i, parent in enumerate(taxonomy.parents(word, recursive=True)[::-1]))
	print 'CHILDREN:\n', ''.join('%s(%s) %s\n' % (' '*i, i, parent) for i, parent in enumerate(taxonomy.children(word, recursive=True)))