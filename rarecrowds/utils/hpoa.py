import os
import pickle
import pandas as pd
from typing import Dict, List


class Hpoa:
    """Read data from HPOA file or stored pickle file."""

    def __init__(self, reload: bool = False):
        """
        Load disease annodation data.
        If filepath is not provided, load pickle data.
        Alternatively, load HPOA data file (tsv).
        """
        self._data_path = os.path.join(os.path.dirname(__file__), "_data")
        filepath = os.path.join(self._data_path, "phenotype.hpoa.pkl")
        if reload:
            try:
                self.data = self._load_anns(filepath)
            except ValueError as ex:
                print(
                    "The HPOA file has unexpected data. You need to edit the parsing."
                )
                print(ex)
            else:
                self._save(filepath)
        else:
            with open(filepath, "rb") as fp:
                self.data = pickle.load(fp)

        self.hpos = self._load_hpos(self.data)

    def __str__(self) -> str:
        return self.data

    def _load_anns(self, filename: str) -> Dict[str, List[str]]:
        """
        Load HPOA file provided through the constructor method.
        """
        d = {}
        df = pd.read_csv(filename, header=4, sep="\t")
        gb = df.groupby(["#DatabaseID"])
        for disease, group in gb:
            disease = disease.upper()
            d[disease] = {}
            for _, row in group.iterrows():
                # Get disease name
                d[disease].setdefault("name", row["DiseaseName"])
                # Get HPO annotation. Can be Phenotype (P) or other entity
                if row["Aspect"] == "P":
                    # See if HP term is negated
                    if pd.isna(row["Qualifier"]):
                        d[disease] = self.__add_phenotype_annotation(
                            d[disease], "phenotype", row
                        )
                    elif row["Qualifier"].lower() == "not":
                        d[disease].setdefault("notPhenotype", {})
                        d[disease]["notPhenotype"][row["HPO_ID"]] = []
                        if pd.notna(row["Modifier"]):
                            s = "There was a modifier found attached to a phenotype marked as NOT present:\n"
                            s += row.to_string()
                            raise ValueError(s)
                    else:
                        s = "There was a qualifier found different from NOT:\n"
                        s += row.to_string()
                        raise ValueError(s)
                # Get clinical course, modifier and inheritance of the disease
                elif row["Aspect"] == "C":
                    d[disease] = self.__add_disease_annotation(
                        d[disease], "clinicalCourse", row
                    )
                elif row["Aspect"] == "M":
                    d[disease] = self.__add_disease_annotation(
                        d[disease], "clinicalModifier", row
                    )
                elif row["Aspect"] == "I":
                    d[disease] = self.__add_disease_annotation(
                        d[disease], "inheritance", row
                    )
                else:
                    s = "There was an unknown aspect found:\n"
                    s += row.to_string()
                    raise ValueError(s)
        return d

    @staticmethod
    def __add_phenotype_annotation(
        d: Dict[str, List[str]], field: str, row
    ) -> Dict[str, List[str]]:
        hp = row["HPO_ID"]
        # Add HP term
        d.setdefault(field, {})
        d[field].setdefault(hp, {})
        # Add modifiers
        for col in ["frequency", "modifier", "onset", "sex"]:
            if pd.notna(row[col]):
                d[field][hp][col] = row[col]
        return d

    @staticmethod
    def __add_disease_annotation(d, field, row):
        d.setdefault(field, [])
        d[field].append(row["HPO_ID"])
        if pd.notna(row["Modifier"]):
            d[field].append(row["Modifier"])
        return d

    def _load_hpos(self, anns: dict) -> List[str]:
        """
        Get sorted list of used HPO terms in disease annotations.
        """
        items = set()
        for disease in anns:
            for hp in list(anns[disease]["phenotype"].keys()):
                items.add(hp)
        res = list(items)
        res.sort()
        return res

    def __getitem__(self, disease: str) -> List[str]:
        """Get disease data."""
        try:
            disease = disease.upper()
            return self.data[disease]
        except:
            return None

    def diseases_by_phens(self, hpos: list) -> List[str]:
        """Get diseases with given symptom(s)."""
        items = set()
        for hp in hpos:
            for disease in self.data:
                if hp in self.data[disease]:
                    items.add(disease)
        res = list(items)
        res.sort()
        return res

    def _save(self, path: str) -> None:
        """Store HPOA file in pickle file."""
        with open(path, "wb") as fp:
            pickle.dump(self.data, fp)
