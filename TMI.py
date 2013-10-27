import codecs
import cPickle
import math
import re
import networkx as nx

from itertools import ifilter
from operator import itemgetter

from pattern.en import parsetree, wordnet
from pattern.search import taxonomy, search, Classifier, Pattern


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

# /////////////////////////////////////////////////////////////////////////////
# Interface classes on the TMI
# /////////////////////////////////////////////////////////////////////////////

def main_category_motif(motif):
    "Return true if the motif is one of the general categories ABC...XYZ."
    number, description = motif
    return description.isupper() and number.isalpha()


class TMI(nx.DiGraph):
    """Thompson's Motif Index represented as a hierarchical
    Dirrected Graph in networkx."""

    def __init__(self, data=None, **attr):
        nx.DiGraph.__init__(self, data=None, **attr)
        self._subsumers = {} # memoizing dictionary

    def subsumers(self, node, weight=None):
        "Return the subsumers of a node."
        if node in self._subsumers: return self._subsumers[node]
        subsumers = nx.shortest_path_length(self, node, weight=weight)
        self._subsumers[node] = subsumers
        return subsumers

    def parents(self, node):
        "Return the parents of a node."
        parents = self.subsumers(node)
        subsumers = [parent for parent in sorted(parents, key=parents.__getitem__)]
        subsumers.remove(node)
        assert 'ROOT' in subsumers, (node, subsumers)
        return subsumers

    def children(self, node):
        "Return the parents of a node."
        return set(self.predecessors(node))

    def common_subsumers(self, a, b, weight='weight'):
        "Return all common subsumers between two nodes a and b."
        subsumers_a = self.subsumers(a, weight=weight)
        subsumers_b = self.subsumers(b, weight=weight)
        return {k: v for k, v in subsumers_a.iteritems() if k in subsumers_b}

    def lowest_common_subsumer(self, a, b):
        "Return the lowest common subsumer between two nodes."
        return min(self.common_subsumers(a, b).iteritems(), key=itemgetter(1))

    def distance_between(self, a, b):
        """Return the distance between a and b in terms of their 
        lowest common subsumer."""
        return self.lowest_common_subsumer(a, b)[1] 

    def search(self, pattern):
        for node, data in self.nodes(data=True):
            if search(pattern, data['parse']):
                yield node, data['data']


# /////////////////////////////////////////////////////////////////////////////
# Functions to compile the TMI into a Directed Graph
# /////////////////////////////////////////////////////////////////////////////

def split_index_entry(entry):
    "Split entries in the TMI index (not motifs...)."
    return re.split('\.(?=[^-])', entry.strip(), maxsplit=1)

def compile_index(index):
    """Function that provides the basic graph in which we will insert
    the motifs from the TMI."""
    headers, header, headerchange, history = [], None, False, []
    G = TMI() # initialize a Directed Graph
    for entry in index:
        motif = (number, description) = split_index_entry(entry)
        G.add_node(number, data=description, parse=parsetree(description, lemmata=True), anchor=True)
        if main_category_motif(motif):
            # we found a new anchor point
            header, headerchange = number, True
            headers.append(number)
        elif '-' in number: # motif declaring a range.
            # collect the lower and upper bounds
            lower, upper = [integer(m) for m in number.split('.-')]
            if headerchange:
                G.add_edge(header, number)
                headerchange = False
                history = []
            else:
                # there could be sub-anchors, check and apply
                while history and upper > integer(history[-1].split('.-')[1]):
                    history.pop()
                if history: # if there still is some history, it is a subanchor
                    G.add_edge(history[-1], number)
                else:
                    G.add_edge(header, number)
            history.append(number)
        else:
            while history and integer(number) > integer(history[-1].split('.-')[1]):
                history.pop()
            G.add_edge(history[-1], number)
    G.add_node('ROOT', data='Unobserved ROOT node of the TMI', parse='')
    # connect all header categories to an fictious root node.
    for header in headers:
        G.add_edge('ROOT', header)
    return G

def integer(number):
    if '.-' in number: number = number.split('.-')[0]
    return int(number[1:])

def spell_out_nodes(node):
    "Return all parent nodes of this motif."
    elts = node.split('.')
    if len(elts) == 1:
        return elts
    return ['.'.join(elts[:i]) for i in xrange(1, len(elts)) if elts[i-1] != '0']
    
def rounddown(node, i=100.0):
    "Rounddown the motif number to the nearest 10th or 100th."
    if i == 200:
        return node[0] + str(integer(rounddown(node))-100)
    return "%s%d" % (node[0], int(math.floor(integer(node) / float(i))) * i)

def find_closest_anchor(number, index):
    candidates = [m for m,data in index.nodes(data=True) if 'anchor' in data
                  and not m.isalpha() and m[0] == number[0] 
                  and integer(number) >= integer(m) 
                  and integer(number) <= (integer(m.split('.-')[1]) if '.-' in m else integer(number))]
    return min(candidates, key=lambda m: abs(integer(number) - integer(m)))

def add_motifs_to_index(motifs, index):
    "Function to add the motifs from the TMI to the index."
    for motif in motifs:
        motif = (number, description) = motif.strip().split('\t')
        print 'Adding: ', number
        if number.endswith('.'): number = number[:-1]
        # it could be we have already seen this motif in the index
        # if so, continue to the next
        if number in index: continue
        index.add_node(number, data=description, parse=parsetree(description, lemmata=True))
        if len(number.split('.')) is 1: # non-terminal node
            # try to match the motif to one of the motifs in the index
            if rounddown(number, 10) != number and rounddown(number, 10) in index:
                index.add_edge(rounddown(number, 10), number)
            elif rounddown(number) != number and rounddown(number) in index:
                anchor = find_closest_anchor(number, index)
                if integer(anchor) > integer(rounddown(number)):
                    index.add_edge(anchor, number)
                else:
                    assert rounddown(number) in index, number
                    index.add_edge(rounddown(number), number)
            # if still no luck... This means trouble
            else:
                best = find_closest_anchor(number, index)
                index.add_edge(best, number)
        else:
            parents = spell_out_nodes(number)
            if parents[-1] not in index:
                # there are a few inconsistencies in the TMI where terminal
                # nodes do not have a direct parent. We add them to their next
                # most direct parent.
                if rounddown(parents[-1], 10) in index:
                    index.add_edge(rounddown(parents[-1], 10), number)
                elif rounddown(parents[-1]) in index:
                    index.add_edge(rounddown(parents[-1]), number)
                else:
                    raise ValueError('Could not resolve parent of %s' % motif)
            else:
                index.add_edge(parents[-1], number)
    return index

def normalize_step_weight(graph):
    "Changes the edge weights in the graph proportional to the longest path."
    longest_path_len = max(nx.shortest_path_length(graph, 'ROOT').values())
    # add normalized path length as weight to edges.
    for category in 'ABCEDFGHJKLMNPQRSTUVWXZ':
        # for each category, find out how long the longest path is.
        cat_longest_path_len = max(nx.shortest_path_length(graph, category).values()) + 1
        # normalize the stepsize
        stepsize = float(longest_path_len) / cat_longest_path_len
        # traverse tree for this category and assign stepsize to edges as weight attribute
        for a,b in nx.dfs_edges(graph, category):
            graph[a][b]['weight'] = stepsize

if __name__ == '__main__':
    with codecs.open('tmi-index.txt', encoding='utf-8') as inf:
        index = compile_index(inf)
    with codecs.open('tmi-cleaned.txt', encoding='utf-8') as inf:
        tmi = add_motifs_to_index(inf, index)
    normalize_step_weight(tmi)
    tmi.reverse(copy=False)
    with open('tmi.cPickle', 'w') as out:
        cPickle.dump(tmi, out)

