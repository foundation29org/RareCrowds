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

    def plot_disease(self, patient: Dict, name: str = "", code: str = ""):
        def prepare_data(G, disease_set):
            mapping = {n: n.replace(":", "_") for n in G.nodes}
            G = nx.relabel_nodes(G, mapping)
            pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")
            data = {
                "edges": {"x": [], "y": []},
                "preds": {"x": [], "y": [], "labels": []},
                "phens": {"x": [], "y": [], "labels": []},
            }
            for edge in G.edges:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                data["edges"]["x"].append(x0)
                data["edges"]["x"].append(x1)
                data["edges"]["x"].append(None)
                data["edges"]["y"].append(y0)
                data["edges"]["y"].append(y1)
                data["edges"]["y"].append(None)
            for node in G.nodes:
                x, y = pos[node]
                label = self[node.replace("_", ":")]
                label = f"{label['id']}: {label['label']}"
                if node.replace("_", ":") in disease_set:
                    data["phens"]["x"].append(x)
                    data["phens"]["y"].append(y)
                    data["phens"]["labels"].append(label)
                else:
                    data["preds"]["x"].append(x)
                    data["preds"]["y"].append(y)
                    data["preds"]["labels"].append(label)
            return data

        if type(patient) == list:
            patient = {"phenotype": patient}
        elif type(patient) == dict and not patient.get("phenotype"):
            patient = {"phenotype": patient}

        patient_set = set(patient["phenotype"])
        hpo_set = patient_set.union(set(self.predecessors(list(patient_set), 1000)))
        hpo_set.remove("HP:0000001")
        G = self.Graph.subgraph(list(hpo_set))

        plt_data = prepare_data(G, patient_set)

        edge_trace = go.Scatter(
            x=plt_data["edges"]["x"],
            y=plt_data["edges"]["y"],
            name="HPO links",
            line=dict(width=0.75, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        pred_trace = go.Scatter(
            x=plt_data["preds"]["x"],
            y=plt_data["preds"]["y"],
            name="Predecessor terms",
            text=plt_data["preds"]["labels"],
            mode="markers",
            marker=dict(color="#888", size=5, line_width=0),
        )

        terms_trace = go.Scatter(
            x=plt_data["phens"]["x"],
            y=plt_data["phens"]["y"],
            name="Input terms",
            mode="markers",
            text=plt_data["phens"]["labels"],
            marker=dict(size=10, line_width=1),
        )

        fig = go.Figure(
            data=[edge_trace, pred_trace, terms_trace],
            layout=go.Layout(
                width=1000,
                height=600,
                showlegend=True,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        if not name:
            name = patient.get("name")
        if not code:
            code = patient.get("id")
        if name or code:
            title = "HPO terms"
            if name:
                title += f" of {name}"
            if code:
                if "orpha" in code.lower():
                    link = (
                        "http://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert="
                    )
                    link += code.split(":")[1]
                elif "omim" in code.lower():
                    link = "https://www.omim.org/entry/"
                    link += code.split(":")[1]
                elif "mondo" in code.lower():
                    link = "https://monarchinitiative.org/disease/"
                    link += code.upper()
                title += f" <a href='{link}'>({code})</a>"
            fig.update_layout(title=title, titlefont_size=14)
        fig.show()
        return fig

    def plot_patient(self, patient=None, disease=None):

        if not disease:
            return self.plot_disease(patient)

        if not patient:
            return self.plot_disease(
                disease.get("phenotype"), disease.get("name"), disease.get("id")
            )

        if type(patient) == list:
            patient = {"phenotype": patient}
        elif type(patient) == dict and not patient.get("phenotype"):
            patient = {"phenotype": patient}

        if type(disease) == list:
            disease = {"phenotype": disease}
        elif type(disease) == dict and not disease.get("phenotype"):
            disease = {"phenotype": disease}

        def prepare_data(G, patient_set, disease_set):
            ## Calculate positions
            ## The dot program does not handle : characters in the ids...
            mapping = {n: n.replace(":", "_") for n in G.nodes}
            G = nx.relabel_nodes(G, mapping)
            pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")
            ## Set positions of each item
            data = {
                "edges": {"x": [], "y": []},
                "preds": {"x": [], "y": [], "labels": []},
                "patient": {"x": [], "y": [], "labels": []},
                "disease": {"x": [], "y": [], "labels": []},
                "both": {"x": [], "y": [], "labels": []},
            }
            for edge in G.edges:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                data["edges"]["x"].append(x0)
                data["edges"]["x"].append(x1)
                data["edges"]["x"].append(None)
                data["edges"]["y"].append(y0)
                data["edges"]["y"].append(y1)
                data["edges"]["y"].append(None)
            for node in G.nodes:
                x, y = pos[node]
                old_node = node.replace("_", ":")
                label = self[old_node]
                label = f"{label['id']}: {label['label']}"
                if (old_node in patient_set) and (old_node in disease_set):
                    data["both"]["x"].append(x)
                    data["both"]["y"].append(y)
                    data["both"]["labels"].append(label)
                elif old_node in patient_set:
                    data["patient"]["x"].append(x)
                    data["patient"]["y"].append(y)
                    data["patient"]["labels"].append(label)
                    # print('pat:', old_node)
                elif old_node in disease_set:
                    data["disease"]["x"].append(x)
                    data["disease"]["y"].append(y)
                    data["disease"]["labels"].append(label)
                else:
                    data["preds"]["x"].append(x)
                    data["preds"]["y"].append(y)
                    data["preds"]["labels"].append(label)
            return data

        hpo_set = set()
        ## Get patient set
        patient_set = set(patient["phenotype"])
        hpo_set = hpo_set.union(
            patient_set.union(set(self.predecessors(list(patient_set), 1000)))
        )
        ## Get disease set
        disease_set = set(disease["phenotype"])
        hpo_set = hpo_set.union(
            disease_set.union(set(self.predecessors(list(disease_set), 1000)))
        )
        ## Get subgraph
        hpo_set.remove("HP:0000001")
        G = self.Graph.subgraph(list(hpo_set))
        ## Prepare the data
        plt_data = prepare_data(G, patient_set, disease_set)

        edge_trace = go.Scatter(
            x=plt_data["edges"]["x"],
            y=plt_data["edges"]["y"],
            name="HPO links",
            line=dict(width=0.75, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        pred_trace = go.Scatter(
            x=plt_data["preds"]["x"],
            y=plt_data["preds"]["y"],
            name="Predecessor terms",
            text=plt_data["preds"]["labels"],
            mode="markers",
            marker=dict(color="#888", size=5, line_width=0),
        )

        both_trace = go.Scatter(
            x=plt_data["both"]["x"],
            y=plt_data["both"]["y"],
            name="Common terms",
            mode="markers",
            text=plt_data["both"]["labels"],
            marker=dict(size=10, line_width=1),
        )

        disease_trace = go.Scatter(
            x=plt_data["disease"]["x"],
            y=plt_data["disease"]["y"],
            name=disease.get("name", "Disease terms"),
            mode="markers",
            text=plt_data["disease"]["labels"],
            marker=dict(size=10, line_width=1),
        )

        patient_trace = go.Scatter(
            x=plt_data["patient"]["x"],
            y=plt_data["patient"]["y"],
            name=patient.get("name", "Patient terms"),
            mode="markers",
            text=plt_data["patient"]["labels"],
            marker=dict(size=10, line_width=1),
        )

        fig = go.Figure(
            data=[edge_trace, pred_trace, both_trace, patient_trace, disease_trace],
            layout=go.Layout(
                width=1000,
                height=600,
                showlegend=True,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        name = disease.get("name")
        code = disease.get("id")
        if name or code:
            title = "HPO comparison"
            if name:
                title += f" of a {name} patient"
            if code:
                if "orpha" in code.lower():
                    link = (
                        "http://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert="
                    )
                    link += code.split(":")[1]
                elif "omim" in code.lower():
                    link = "https://www.omim.org/entry/"
                    link += code.split(":")[1]
                elif "mondo" in code.lower():
                    link = "https://monarchinitiative.org/disease/"
                    link += code.upper()
                title += f" <a href='{link}'>({code})</a>"
            fig.update_layout(title=title, titlefont_size=14)
        fig.show()
        return fig
