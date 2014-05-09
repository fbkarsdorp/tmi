
import copy
from whoosh.qparser.plugins import Plugin
from whoosh.qparser import QueryParser
from whoosh.qparser import syntax
from pattern.en import wordnet as WN

def expand(term, limit=3):
    # EXPANSION IS ONLY DONE FOR FIRST SYNSET. WHY?
    try:
        hypernyms = WN.synsets(term, 'NN')[0].hypernyms(recursive=True)
        return {w.senses[0] for w in hypernyms[:limit]}.union({term})
    except IndexError:
        return {}

class WordnetPlugin(Plugin):

    def __init__(self, fieldnames, fieldboosts=None, expansion=3, group=syntax.OrGroup.factory(0.9)):

        self.fieldnames = fieldnames
        self.boosts = fieldboosts or {}
        self.expansion = expansion
        self.group = group

    def filters(self, parser):
        # Run after the fields filter applies explicit fieldnames (at priority
        # 100)
        return [(self.do_multifield, 110)]

    def do_multifield(self, parser, group):
        for i, node in enumerate(group):
            if isinstance(node, syntax.GroupNode):
                # Recurse inside groups
                group[i] = self.do_multifield(parser, node)
            elif node.has_fieldname and node.fieldname is None:
                # For an unfielded node, create a new group containing fielded
                # versions of the node for each configured "multi" field.
                newnodes = []
                for fname in self.fieldnames:
                    print fname
                    newnode = copy.copy(node)
                    newnode.set_fieldname(fname)
                    newnode.set_boost(self.boosts.get(fname, 1.0))
                    newnodes.append(newnode)
                for hypernym in expand(node.text, self.expansion):
                    newnode = copy.copy(node)
                    newnode.set_fieldname("wn")
                    newnode.text = hypernym
                    newnode.set_boost(self.boosts.get("wn", 1.0))
                    newnodes.append(newnode)                    
                group[i] = self.group(newnodes)
            elif node.has_fieldname and node.fieldname == 'wn':
                node.set_boost(self.boosts["description"])
                group[i] = node
        return group

def MultiFieldWordNetParser(fieldnames, schema, fieldboosts=None, expansion=1, **kwargs):
    p = QueryParser(None, schema, **kwargs)
    mfp = WordnetPlugin(fieldnames, fieldboosts=fieldboosts, expansion=expansion)
    p.add_plugin(mfp)
    return p
