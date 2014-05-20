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

@app.route('/download', methods=['GET', 'POST'])
def download():
    ix = whoosh.index.open_dir('index', indexname='tmi')
    with ix.searcher() as searcher:
        def _search(query):
            parser = MultiFieldWordNetParser(["description", "additional"], ix.schema,
                fieldboosts={'description': 3.0, 'additional': 1.0}, 
                group=qparser.OrGroup.factory(0.9))
            parsed_query = parser.parse(query)
            return searcher.search(parsed_query, limit=None, terms=True)

        def to_json(hits):
            hits.fragmenter = WholeFragmenter()
            for hit in hits:
                result = {'motif': hit['motif'],
                          'description': hit.highlights('description', minscore=0),
                          'additional': hit.highlights('additional', minscore=0),
                          'references': hit['references'].strip()}
                yield result

        q = request.args.get('q')
        results = _search(q.strip())
        found = len(results)
        json_results = list(to_json(results))
        return jsonify({'results': json_results, 
                        'hits': found, 
                        'time': results.runtime})

# views:
@app.route('/api', methods=['GET', 'POST'])
def api():
    ix = whoosh.index.open_dir('index', indexname='tmi')
    with ix.searcher() as searcher:
        def _search(query,page):
            parser = MultiFieldWordNetParser(["description", "additional"], ix.schema,
                fieldboosts={'description': 3.0, 'additional': 1.0}, 
                group=qparser.OrGroup.factory(0.9))
            parsed_query = parser.parse(query)
            return searcher.search_page(parsed_query, page, pagelen=20, terms=True)

        def to_json(hits):
            hits.results.fragmenter = WholeFragmenter()
            for hit in hits:
                result = {'motif': hit['motif'],
                          'description': hit.highlights('description', minscore=0),
                          'additional': hit.highlights('additional', minscore=0),
                          'references': hit['references'].strip()}
                yield result
        q = json.loads(request.data)['q']
        page = json.loads(request.data).get('page') or 1
        logging.info("QUERY: " + q.strip())
        results = _search(q.strip(),page)
        found = len(results)
        # html_results = htmlize(results)
        json_results = list(to_json(results))
        suggestion = results.results.key_terms('wn', numterms=3)
        if suggestion:
            suggestion = [w for w, _ in suggestion]
            # suggestion = "More abstraction? Try one of these: " + ', '.join('wn:%s' % w for w, _ in suggestion)
        else:
            suggestion = []
        return jsonify({'results': json_results, 
                        'hits': found, 
                        'pagecount': results.pagecount,
                        'time': results.results.runtime, 
                        'suggest': suggestion})
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html', title='TMI-search')

if __name__ == '__main__':
    app.run(debug=True,host='plot',port=5555,use_reloader=True,threaded=True)



