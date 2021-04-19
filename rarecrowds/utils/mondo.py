import os
import pickle
import networkx as nx

from rarecrowds.utils.ontograph import OntoGraph


class Mondo(OntoGraph):
    """Class to load the MONDO ontology."""

    def __init__(self, filename=None, update=False):
        self.mapping = {}
        self.xrefs = {}
        self.purl = "http://purl.obolibrary.org/obo/mondo.obo"
        _data_path = os.path.join(os.path.dirname(__file__), "_data")
        _pkl_path = os.path.join(_data_path, "mondo.pkl")
        if update:
            filename = self.purl
            if filename:
                print(f"Warning! 'filename' is repalced by '{self.purl}'")
        elif not filename:
            filename = _pkl_path
        super().__init__(filename)
        if update:
            super().save(_pkl_path)

    def _load_graph(self, filename):
        with open(filename, "rb") as fp:
            meta = pickle.load(fp)
        self.mapping = meta["alias"]
        return meta["graph"]

    def _add_node(self, G, id, term):
        self.mapping[id] = id
        if not id in self.xrefs:
            self.xrefs[id] = []
        for xref in term.xrefs:
            self.mapping[xref.id] = id
            self.xrefs[id].append(xref.id)
        # G.add_node(id, name=term.name, desc=str(term.definition), comment=self._parse_comment(term), synonyms=self._parse_synonyms(term))
        G.add_node(id, id=id, label=term.name.strip())

    def _add_edge(self, G, id, term):
        if id.startswith("MONDO"):
            for sub in term.subclasses(1):
                if sub.id != term.id:
                    G.add_edge(term.id, sub.id)

    def alias(self, id):
        try:
            id = id.upper()
            return self.mapping[id]
        except:
            return None

    def aliases(self, ids):
        items = []
        for id in ids:
            id = self.alias(id)
            if id:
                items.append(id)
        return items

    def save(self, path):
        meta = {"graph": self.Graph, "alias": self.mapping}
        with open(path, "wb") as fp:
            pickle.dump(meta, fp)
