# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify
from TMI import TMI
import cPickle as pickle

#flask application
app = Flask(__name__)

with open("tmi.cPickle") as inf:
	tmi = pickle.load(inf)

# views:
@app.route('/api',methods=['GET', 'POST'])
def api():

	query = request.form['q']

	results = ""
	for match in tmi.search(query):
		idee = match[0]
		text = match[1]
		results += "<div id='match'><span id='idee'>"+idee+"</span><span id='text'>"+text+"</span></div>"
	return jsonify({"html":results})

@app.route('/')
def index():
	return open(os.getcwd()+'/static/templates/index.html').read()

if __name__ == '__main__':
	app.run(debug=True,host='localhost',port=5555,use_reloader=True,threaded=False)




