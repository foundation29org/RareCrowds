import glob
import os

from rarecrowds.phenopackets_pb2 import Phenopacket
from rarecrowds.rarecrowds import PhenotypicDatabase


def test_add_phenopacket():
    testPhenopacket = Phenopacket()
    testPhenopacket.id = "testId"
    testDB = PhenotypicDatabase()
    testDB.add_phenopacket(testPhenopacket)
    assert testDB.db["testId"] == testPhenopacket


def test_add_hpo_symptoms():
    testDB = PhenotypicDatabase()
    list_of_dicts = [{"phenotypicFeatures": [{"type": {"id": "HP:00675"}}]}]
    testDB.add_hpo_symptoms(list_of_dicts)
    assert list_of_dicts == [
        {
            "phenotypicFeatures": [{"type": {"id": "HP:00675"}}],
            "hpo terms": ["HP:00675"],
        }
    ]


def test_load_from_file():
    test_file_path = "test/resources/test_phenopacket.json"
    testDB = PhenotypicDatabase()
    phenopacket = testDB.load_from_file(test_file_path)
    assert "test_phenopacket" == phenopacket.id
    assert "test_subject" == phenopacket.subject.id
    assert phenopacket.phenotypic_features[0].type.id == "HP:0011516"
    assert (
        phenopacket.phenotypic_features[0].evidence[0].evidence_code.id == "ECO:0000033"
    )
    assert (
        phenopacket.phenotypic_features[0].evidence[0].evidence_code.label
        == "author statement supported by traceable reference"
    )
    assert (
        phenopacket.phenotypic_features[0].evidence[0].reference.id == "PMID:32340307"
    )
    assert phenopacket.genes[0].symbol == "CNGB3"
    assert phenopacket.diseases[0].term.label == "Achromatopsia"


def test_load_from_folder():
    test_file_path = "test/resources"
    testDB = PhenotypicDatabase()
    testDB.load_from_folder(test_file_path)
    assert "test_phenopacket" in testDB.db.keys()
    phenopacket = testDB.db["test_phenopacket"]
    assert "test_phenopacket" == phenopacket.id
    assert "test_subject" == phenopacket.subject.id
    assert phenopacket.phenotypic_features[0].type.id == "HP:0011516"
    assert (
        phenopacket.phenotypic_features[0].evidence[0].evidence_code.id == "ECO:0000033"
    )
    assert (
        phenopacket.phenotypic_features[0].evidence[0].evidence_code.label
        == "author statement supported by traceable reference"
    )
    assert (
        phenopacket.phenotypic_features[0].evidence[0].reference.id == "PMID:32340307"
    )
    assert phenopacket.genes[0].symbol == "CNGB3"
    assert phenopacket.diseases[0].term.label == "Achromatopsia"


def test_load_default():
    testDB = PhenotypicDatabase()
    testDB.load_default("kleyner-2016")
    assert os.path.exists("rarecrowds_data/kleyner-2016")
    assert len(glob.glob("rarecrowds_data/kleyner-2016/*.json")) == 1
