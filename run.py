# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify
from tmi import find
import cPickle as pickle


#flask application
app = Flask(__name__)

with open("tmi.cPickle") as inf:
	tmi = []
	while True:
		try:
			motif = pickle.load(inf)
			tmi.append(motif)
		except EOFError:
			break

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



