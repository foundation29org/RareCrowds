import json
import os
from typing import Dict, List

from google.protobuf.json_format import Parse, MessageToJson
import pandas as pd

from rarecrowds.phenopackets_pb2 import Phenopacket


class PhenotypicDatabase:
    def __init__(self):
        self.db = {}
        self.fields = ["id", "phenotypicFeatures", "genes", "diseases", "subject.id"]

    def add_phenopacket(self, phenopacket: Phenopacket):
        self.db[phenopacket.id] = phenopacket

    def load_from_file(self, file_path: str) -> Phenopacket:
        with open(file_path, "r") as jsfile:
            return Parse(message=Phenopacket(), text=jsfile.read())

    def load_from_folder(self, folder_path: str):
        for file in os.listdir(folder_path):
            self.add_phenopacket(self.load_from_file(os.path.join(folder_path, file)))

    def generate_list_of_dicts(self) -> List[Dict]:
        return_list = []
        for k, v in self.db.items():
            return_list.append(json.loads(MessageToJson(v)))
        return return_list

    def generate_dataframe(self) -> pd.core.frame.DataFrame:
        json_list = []
        for k, v in self.db.items():
            json_list.append(json.loads(MessageToJson(v)))
        df = pd.json_normalize(json_list)
        return df[self.fields]
