# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify
import cPickle as pickle

from pattern.en import Sentence
from tmi import find


#flask application
app = Flask(__name__)

tmi = []
for line in open('tmi.txt'):
    line = line.strip().split('\t')
    if len(line) == 3:
        motif, description, parse = line[0], line[1], Sentence(line[2])
        tmi.append((motif, description, parse))

# views:
@app.route('/api',methods=['GET', 'POST'])
def api():

    query = request.form['q'].strip()

    results = ""
    for match in find(query, tmi):
        idee = match[0]
        text = match[1]
        results += "<div id='match'><span id='idee'>"+idee+"</span><span id='text'>"+text+"</span></div>"
    return jsonify({"html":results})

@app.route('/')
def index():
    return open(os.getcwd()+'/static/templates/index.html').read()

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=5555,use_reloader=False,threaded=False)



