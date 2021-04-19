import os
import json
import pickle
import networkx as nx
import networkx.readwrite.json_graph as js

from pronto import Ontology


class OntoGraph:
    def __init__(self, filename):
        if filename.lower()[-4:] == ".pkl":
            self.Graph = self._load_graph(filename)
        else:
            self.Graph = self._build_graph(Ontology(filename))
            _data_path = os.path.join(os.path.dirname(__file__), "_data")
            _pkl_file = os.path.join(_data_path, "hp.pkl")
            self.save(_pkl_file)
        self.root = [nd for nd, d in self.Graph.in_degree() if d == 0][0]

    def _load_graph(self, filename):
        return nx.read_gpickle(filename)

    def _build_graph(self, ontology):
        G = nx.DiGraph()
        for id in ontology:
            term = ontology[id]
            if not term.obsolete:
                self._add_node(G, id, term)
                self._add_edge(G, id, term)
        return G

    def _add_node(self, G, id, term):
        G.add_node(
            id,
            label=term.name,
            desc=str(term.definition),
            comment=self._parse_comment(term),
            synonyms=self._parse_synonyms(term),
        )

    def _add_edge(self, G, id, term):
        for sub in term.subclasses(1):
            if sub.id != term.id:
                G.add_edge(term.id, sub.id)

    def _parse_comment(self, term):
        return term.comment if term.comment else ""

    def _parse_synonyms(self, term):
        syns = []
        for synom in term.synonyms:
            syn = {
                "label": synom.description,
                "scope": synom.scope,
                "type": synom.type.id if synom.type else None,
                "xrefs": [xr.id for xr in synom.xrefs] if synom.xrefs else None,
            }
            syns.append(syn)
        return syns

    @property
    def items(self):
        return self.Graph.nodes

    def __getitem__(self, id):
        try:
            id = id.upper()
            return self.Graph.nodes[id]
        except:
            return None

    def save(self, path):
        nx.write_gpickle(self.Graph, path)

    def save_json(self, filename):
        with open(filename, "w") as fp:
            fp.write(self.json())

    def json(self):
        g = js.node_link_data(self.Graph)
        return json.dumps(g)

    def json_adjacency(self):
        g = js.adjacency_data(self.Graph)
        return json.dumps(g)

    def successors(self, ids, depth=1):
        if not type(ids) is list:
            ids = [ids]
        items = set()
        for id in ids:
            for item in self._successors(id, depth):
                items.add(item)
        res = list(items)
        res.sort()
        return res

    def _successors(self, id, depth):
        depth -= 1
        items = set()
        for item in self.Graph.successors(id):
            items.add(item)
            if depth != 0:
                for it in self._successors(item, depth):
                    items.add(it)
        return items

    def predecessors(self, ids, depth=1):
        if not type(ids) is list:
            ids = [ids]
        items = set()
        for id in ids:
            for item in self._predecessors(id, depth):
                items.add(item)
        res = list(items)
        res.sort()
        return res

    def _predecessors(self, id, depth):
        depth -= 1
        items = set()
        if self.Graph.has_node(id):
            for item in self.Graph.predecessors(id):
                items.add(item)
                if depth != 0:
                    for it in self._predecessors(item, depth):
                        items.add(it)
        return items
