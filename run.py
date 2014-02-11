# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, Response, stream_with_context, render_template
from pattern.en import wordnet as WN
import whoosh
from whoosh import index
from whoosh import qparser
import codecs
import re

from collections import defaultdict

import json


#flask application
app = Flask(__name__)

# views:
@app.route('/api', methods=['GET', 'POST'])
def api():
    ix = whoosh.index.open_dir('index', indexname='tmi')
    with ix.searcher() as searcher:
        def _search(query):
            for word in query.split():
                if not word.startswith('wordnet') and not word.isupper():
                    try:
                        hypernyms = WN.synsets(word, 'NN')[0].hypernyms(recursive=True)
                        query += ' wordnet:"%s"' % hypernyms[0][0]
                    except IndexError:
                        pass
            query = qparser.QueryParser(
                "description", ix.schema, group=qparser.OrGroup).parse(query)
            print query
            return searcher.search(query, limit=100)

        def htmlize(hits):
            html = ''
            for hit in hits:
                motif = hit['motif']
                description = hit['description']
                html += "<div id='match'><span id='idee'>%s</b></span><span id='text'>%s</span></div>" % (
                        motif, description)
            return html

        results = htmlize(_search(request.form['q'].strip()))
        return jsonify({'html': results})

@app.route('/')
def index():
    return render_template('index.html', title='TMI-search')

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=5555,use_reloader=True,threaded=True)



