import os
import pickle
from typing import Dict, List
import xml.etree.ElementTree as ET


def _read_node(node):
    d = {}
    for elem in node:
        if len(list(elem)) > 0:
            # Whenever a node has a count attribute, make it a list.
            # Otherwise the key would overwrite each other.
            if "count" in elem.attrib:
                d.setdefault(elem.tag, list())
                for subelem in elem:
                    d[elem.tag].append(_read_node(subelem))
            else:
                d[elem.tag] = {**elem.attrib, **_read_node(elem)}
        else:
            if "count" in elem.attrib:
                # this node is an empty list
                d.setdefault(elem.tag, [])
            else:
                d.setdefault(elem.tag, {})
                if elem.attrib:
                    d[elem.tag].update(elem.attrib)
                if elem.text:
                    d[elem.tag]["Data"] = elem.text
    return d


def _text2HPOfreq(d):
    if d["Name"]["Data"] == "Obligate (100%)":
        return "HP:0040280"
    elif d["Name"]["Data"] == "Very frequent (99-80%)":
        return "HP:0040281"
    elif d["Name"]["Data"] == "Frequent (79-30%)":
        return "HP:0040282"
    elif d["Name"]["Data"] == "Occasional (29-5%)":
        return "HP:0040283"
    elif d["Name"]["Data"] == "Very rare (<4-1%)":
        return "HP:0040284"
    elif d["Name"]["Data"] == "Excluded (0%)":
        return "HP:0040285"
    else:
        s = "There was an unknown frequency value found:\n"
        s += str(d)
        raise ValueError(s)


class Orpha:
    """Read data from XML files."""

    def __init__(self, reload=False):
        """
        Load disease annodation data from Orphanet's XML files
        """
        _data_path = os.path.join(os.path.dirname(__file__), "resources")
        _pkl_file = os.path.join(_data_path, "orphadata_all_prods.pkl")
        if reload:
            try:
                _phenotypes_filename = "orphadata_prod4_phenotypes.xml"
                _prevalence_filename = "orphadata_prod9_epidemiological_prevalence.xml"
                _ages_filename = "orphadata_prod9_epidemiological_ages.xml"

                _phenotypes_path = os.path.join(_data_path, _phenotypes_filename)
                _prevalence_path = os.path.join(_data_path, _prevalence_filename)
                _ages_path = os.path.join(_data_path, _ages_filename)

                phenotypes = self.__read_phenotypes(_phenotypes_path)
                prevalence = self.__read_prevalence(_prevalence_path)
                ages = self.__read_ages(_ages_path)

                self.data = self.__aggregate_data(phenotypes, prevalence, ages)
            except Exception as ex:
                raise ex
            else:
                self.__save(_pkl_file)
        else:
            with open(_pkl_file, "rb") as fp:
                self.data = pickle.load(fp)

    def __str__(self) -> str:
        return str(self.data)

    def __getitem__(self, disease: str) -> List[str]:
        """Get disease data."""
        try:
            return self.data[disease.upper()]
        except:
            return None

    def __aggregate_data(self, phen: Dict, prev: Dict, ages: Dict) -> Dict:
        d = {}
        dbs = {"phen": phen, "prev": prev, "ages": ages}
        # Set of Orpha codes
        codes = (
            set(list(phen.keys()))
            .union(set(list(prev.keys())))
            .union(set(list(ages.keys())))
        )
        for orpha in codes:
            d[orpha] = {}
            # Set of fields in all XMLs
            fields = (
                set(list(phen.get(orpha, {}).keys()))
                .union(set(list(prev.get(orpha, {}).keys())))
                .union(set(list(ages.get(orpha, {}).keys())))
            )
            for field in fields:
                # Iterate over dbs and values to the correspondent field in out dict
                for val in dbs.values():
                    if field not in val.get(orpha, {}):
                        continue
                    if field in d[orpha]:
                        # print(db, field, val[orpha])
                        if d[orpha][field] != val[orpha][field]:
                            s = "New value is different from present field value.\n"
                            s += "New value:\n" + str(val[orpha][field]) + "\n"
                            s += "Present value:\n" + str(d[orpha][field]) + "\n"
                            print(s)
                            raise ValueError(s)
                    d[orpha][field] = val[orpha][field]
        return d

    def __read_ages(self, filepath):
        xmldata = self.__xml2dict(filepath, "DisorderList")

        def add_term(in_d, in_field):
            l = []
            for s in in_d[in_field]:
                l.append(s["Name"]["Data"])
            return l

        d = {}
        for val in xmldata:
            try:
                code = "ORPHA:" + val["OrphaCode"]["Data"]
                d[code] = {
                    "name": val["Name"]["Data"],
                    "link": val["ExpertLink"]["Data"],
                    "type": val["DisorderType"]["Name"]["Data"],
                    "group": val["DisorderGroup"]["Name"]["Data"],
                }
                d[code]["ageOnset"] = add_term(val, "AverageAgeOfOnsetList")
                d[code]["ageDeath"] = add_term(val, "AverageAgeOfDeathList")
                d[code]["inheritance"] = add_term(val, "TypeOfInheritanceList")
            except Exception as ex:
                print(val)
                raise ex
        return d

    def __read_prevalence(self, filepath):
        xmldata = self.__xml2dict(filepath, "DisorderList")

        d = {}
        for val in xmldata:
            try:
                code = "ORPHA:" + val["OrphaCode"]["Data"]
                d[code] = {
                    "name": val["Name"]["Data"],
                    "link": val["ExpertLink"]["Data"],
                    "type": val["DisorderType"]["Name"]["Data"],
                    "group": val["DisorderGroup"]["Name"]["Data"],
                    "prevalence": [],
                }
                for s in val["PrevalenceList"]:
                    d[code]["prevalence"].append(
                        {
                            "type": s["PrevalenceType"]["Name"]["Data"],
                            "source": s["Source"].get("Data"),
                            "qualification": s["PrevalenceQualification"]["Name"][
                                "Data"
                            ],
                            "meanPrev": s["ValMoy"]["Data"],
                            "class": s["PrevalenceClass"]
                            .get("Name", {})
                            .get("Data", {}),
                            "geographic": s["PrevalenceGeographic"]["Name"]["Data"],
                            "validation": {
                                "status": s["PrevalenceValidationStatus"]["Name"][
                                    "Data"
                                ]
                            },
                        }
                    )
            except Exception as ex:
                print(val)
                raise ex
        return d

    def __read_phenotypes(self, filepath):
        xmldata = self.__xml2dict(filepath, "HPODisorderSetStatusList")

        d = {}
        for val in xmldata:
            try:
                # print(val)
                code = "ORPHA:" + val["Disorder"]["OrphaCode"]["Data"]
                d[code] = {
                    "name": val["Disorder"]["Name"]["Data"],
                    "link": val["Disorder"]["ExpertLink"]["Data"],
                    "type": val["Disorder"]["DisorderType"]["Name"]["Data"],
                    "group": val["Disorder"]["DisorderGroup"]["Name"]["Data"],
                    "source": val["Source"].get("Data", {}),
                    "validation": {
                        "status": val["ValidationStatus"].get("Data", {}),
                        "date": val["ValidationDate"].get("Data", {}),
                    },
                    "phenotype": {},
                }
                for s in val["Disorder"]["HPODisorderAssociationList"]:
                    hp = s["HPO"]["HPOId"]["Data"]
                    d[code]["phenotype"][hp] = {}

                    if "HPOFrequency" in s:
                        d[code]["phenotype"][hp]["frequency"] = _text2HPOfreq(
                            s["HPOFrequency"]
                        )
                    if "DiagnosticCriteria" in s:
                        d[code]["phenotype"][hp]["modifier"] = {
                            "diagnosticCriteria": True
                        }

                    if set(s.keys()).difference(
                        {"HPO", "HPOFrequency", "DiagnosticCriteria"}
                    ):
                        temp = "There was a field found different from [HPO, HPOFrequency, DiagnosticCriteria]:\n"
                        temp += str(s)
                        raise ValueError(temp)

            except Exception as ex:
                print(val)
                raise ex
        return d

    def __xml2dict(self, xml_path: str, data_root: str) -> List[Dict]:
        """
        Load XML file provided by Orphanet.
        Iterate over the HPODisorderSetStatusList list, appending disease dicts
        to the list to be returned.
        """
        l = list()
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for elem in root:
            if elem.tag != data_root:
                continue
            for disease_node in elem:
                l.append(_read_node(disease_node))
        return l

    def __save(self, path: str) -> None:
        """Store orphanet's aggregated data in pickle file."""
        with open(path, "wb") as fp:
            pickle.dump(self.data, fp)
