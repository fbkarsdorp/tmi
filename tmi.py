import cPickle

from pattern.en import Sentence, wordnet
from pattern.search import taxonomy, search, Classifier


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

def find(pattern, motifs):
    for motif, description, parse in motifs:
        if search(pattern, parse):
            yield motif, description
        