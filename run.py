# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, Response, stream_with_context, render_template
from pattern.en import wordnet as WN
import whoosh
from whoosh import index
from whoosh import qparser
from whoosh.qparser.plugins import RegexPlugin
import codecs
import re

from collections import defaultdict
from expand import WordnetPlugin, MultiFieldWordNetParser
import json

#flask application
app = Flask(__name__)

formatter = ["<div id='match'> <span id='idee'>%s</span> </br><span id='text'>%s</span>",
             "</br><p id='add'>%s</p>", "<p id='ref'>%s</p>", "</div>"]

# views:
@app.route('/api', methods=['GET', 'POST'])
def api():
    ix = whoosh.index.open_dir('index', indexname='tmi')
    with ix.searcher() as searcher:

        def _search(query):
            parser = MultiFieldWordNetParser(["description", "additional"], ix.schema,
                fieldboosts={'description': 2.0, 'additional': 1.5}, 
                group=qparser.OrGroup.factory(0.9))
            parsed_query = parser.parse(query)
            print parsed_query
            return searcher.search(parsed_query, limit=100)

        def htmlize(hits):
            html = ''
            for hit in hits:
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

        results = htmlize(_search(request.form['q'].strip()))
        return jsonify({'html': results})

@app.route('/')
def index():
    return render_template('index.html', title='TMI-search')

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=5555,use_reloader=True,threaded=True)



