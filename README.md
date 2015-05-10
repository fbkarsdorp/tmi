# TMI: Interface on Thompson's Motif Index

This collection of scripts provides a Python interface to Thompson's Motif Index.
Currently, only python 2.7x is supported.

Dependencies:
- [networkx](http://networkx.github.io)
- [pattern](http://www.clips.ua.ac.be/pattern)
- [flask](http://flask.pocoo.org/)
- [whoosh](https://bitbucket.org/mchaput/whoosh/wiki/Home)
- [ijson](https://pypi.python.org/pypi/ijson/0.8.0)
- [pattern](http://www.clips.ua.ac.be/pages/pattern)

Install with:

    pip install networkx pattern flask whoosh ijson

Next create the index using:

    python indexer.py

Finally start the web servive (locally) using:

    python tmi_run.py

The following can be used as a starting point for a wsgi script to be used with Apache.

    import sys
    import glob
    import os
    
    sys.path.append('/path/to/folder/of/tmi')        
    from tmi.tmi_run import app as application
