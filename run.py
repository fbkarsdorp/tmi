# -*- coding: utf-8 -*-

import os
import logging
import codecs
import json
import re
from collections import defaultdict

from flask import Flask, request, jsonify, Response, stream_with_context, render_template
from pattern.en import wordnet as WN

import whoosh
from whoosh import index
from whoosh import qparser
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
            for hit in hits:
                print hit.matched_terms()
                motif = hit['motif'].strip()
                description = hit['description'].strip()
                additional = hit['additional'].strip()
                references = hit['references'].strip()
                format = formatter[0] % (motif, description)
                if additional:
                    format += formatter[1] % additional
                if references:
                    format += formatter[2] % references
                format += formatter[-1]
                html += format
            return html

        logging.info("QUERY: " + request.form['q'].strip())
        results = _search(request.form['q'].strip())
        found = results.scored_length()
        if results.has_exact_length():
            print("Scored", found, "of exactly", len(results), "documents")
        else:
            low = results.estimated_min_length()
            high = results.estimated_length()
            print("Scored", found, "of between", low, "and", high, "documents")
        html_results = htmlize(results)
        return jsonify({'html': html_results})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    print path
    return render_template('index.html', title='TMI-search')

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=5555,use_reloader=True,threaded=True)



