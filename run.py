# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, Response, stream_with_context, render_template

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

import cPickle as pickle
import codecs

from collections import defaultdict

from pattern.en import Sentence, wordnet
from pattern.search import taxonomy, search, Classifier, Pattern
import json


# /////////////////////////////////////////////////////////////////////////////
# Wordnet Classifier used for searching.
# /////////////////////////////////////////////////////////////////////////////

class WordNetClassifier(Classifier):
    
    def __init__(self, wordnet=None):
        if wordnet is None:
            try: 
                from en import wordnet
            except ImportError:
                pass
        Classifier.__init__(self, self._parents, self._children)
        self.wordnet = wordnet

    def _children(self, word, pos="NN"):
        try: 
            return [w.senses[0] for w in self.wordnet.synsets(word, pos)[0].hyponyms()]
        except (KeyError, IndexError):
            pass
        
    def _parents(self, word, pos="NN"):
        try: 
            return [w.senses[0] for w in self.wordnet.synsets(word, pos)[0].hypernyms()]
        except (KeyError, IndexError):
            pass

taxonomy.classifiers.append(WordNetClassifier(wordnet))


#flask application
app = Flask(__name__)

# views:
@app.route('/api', methods=['GET', 'POST'])
def api():

    query = request.form['q'].strip()
    words = [word for word in query.split() if word.islower()]
    pattern = Pattern.fromstring(query)
    results = ""
    def iterate_tmi():
        for line in codecs.open('tmi.txt', encoding='utf-8'):
            line = line.strip().split('\t')
            if len(line) is not 3:
                continue
            motif, description, parse = line
            if words and not any(word in parse for word in words):
                continue
            if pattern.search(Sentence(parse)):
                yield (motif, description)
    results = ""
    categories = defaultdict(int)
    count = 0
    for motif, description in iterate_tmi():
        results += "<div id='match'><span id='idee'>%s</b></span><span id='text'>%s</span></div>" % (
                        motif, description)
        categories[motif[0]] += 1
        count += 1
    categories = "<div id='count'><span id=hits>Hits:%s</b></span><span id='cats'>%s</span></div>" % (
        count, ' '.join('%s:%s' % (c, f) for c,f in categories.iteritems()))
    return jsonify({'html': results, 'categories': categories})

@app.route('/')
def index():
    return render_template('index.html', title='TMI-search')

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=5555,use_reloader=True,threaded=True)



