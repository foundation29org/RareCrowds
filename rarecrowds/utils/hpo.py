import os
import networkx as nx
import plotly.graph_objects as go
from typing import List, Dict

from rarecrowds.utils.ontograph import OntoGraph


class Hpo(OntoGraph):
    """Class to load the HPO ontology and plot HPO set differences."""

    def __init__(self, filename=None, update=False):
        self.purl = "http://purl.obolibrary.org/obo/hp.obo"
        _data_path = os.path.join(os.path.dirname(__file__), "resources")
        _pkl_path = os.path.join(_data_path, "hp.pkl")
        if update:
            filename = self.purl
            if filename:
                print(f"Warning! 'filename' is repalced by '{self.purl}'")
        elif not filename:
            filename = _pkl_path
        super().__init__(filename)
        if update:
            super().save(_pkl_path)

    def _add_node(self, G, id, term):
        # G.add_node(id, name=term.name, desc=str(term.definition), comment=self._parse_comment(term), synonyms=self._parse_synonyms(term))
        G.add_node(id, id=id, label=term.name)

    def _add_edge(self, G, id, term):
        for sub in term.subclasses(1):
            if sub.id != term.id:
                G.add_edge(term.id, sub.id)

    def simplify(self, ids):
        all_preds = self.predecessors(ids, 1000)
        res = set(ids) - set(all_preds)
        return res
