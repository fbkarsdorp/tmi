# -*- coding: utf-8 -*-

import os
import logging
import codecs
import json
import re
from collections import defaultdict
from functools import partial

from flask import Flask, request, jsonify, Response, stream_with_context, render_template
from pattern.en import wordnet as WN

import whoosh
from whoosh import index
from whoosh import qparser
from whoosh.highlight import WholeFragmenter
from whoosh.qparser.plugins import RegexPlugin

from expand import WordnetPlugin, MultiFieldWordNetParser

#flask application
app = Flask(__name__)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

formatter = ["<div id='match'> <span id='idee'>%s</span> </br><span id='text'>%s</span>",
             "</br><p id='add'>%s</p>", "<p id='ref'>%s</p>", "</div>"]

# views:
@app.route('/api', methods=['GET', 'POST'])
def api():
    ix = whoosh.index.open_dir('index', indexname='tmi')
    with ix.searcher() as searcher:
        def _search(query):
            parser = MultiFieldWordNetParser(["description", "additional"], ix.schema,
                fieldboosts={'description': 3.0, 'additional': 1.0}, 
                group=qparser.OrGroup.factory(0.9))
            parsed_query = parser.parse(query)
            return searcher.search(parsed_query, limit=100, terms=True)

        def htmlize(hits):
            html = ''
            hits.fragmenter = WholeFragmenter()
            for hit in hits:
                motif = hit['motif'].strip()
                additional = hit['additional'].strip()
                references = hit['references'].strip()
                format = formatter[0] % (motif, hit.highlights('description', minscore=0))
                if additional:
                    format += formatter[1] % hit.highlights('additional', minscore=0)
                if references:
                    format += formatter[2] % references
                format += formatter[-1]
                html += format
            return html

        logging.info("QUERY: " + request.form['q'].strip())
        results = _search(request.form['q'].strip())
        found = len(results)
        html_results = htmlize(results)
        suggestion = results.key_terms('wn', numterms=3)
        if suggestion:
            suggestion = "More abstraction? Try one of these: " + ', '.join('wn:%s' % w for w, _ in suggestion)
        else:
            suggestion = ''
        return jsonify({'html': html_results, 
                        'hits': "%s results" % found, 
                        'time': "(%.3f seconds)" % results.runtime, 
                        'suggest': suggestion})

@app.route('/')
def index():
    return render_template('index.html', title='TMI-search')

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=5555,use_reloader=True,threaded=True)



