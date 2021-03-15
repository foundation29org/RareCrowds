import json
import os
from typing import Dict, List

from google.protobuf.json_format import Parse, MessageToJson
import pandas as pd

from rarecrowds.phenopackets_pb2 import Phenopacket
from rarecrowds.utils.azure_utils import download_data

DATA_PATH = "rarecrowds_data"


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
        df = pd.json_normalize(self.generate_list_of_dicts())
        return df[self.fields]

    def load_default(self, dataset: str, data_path: str = DATA_PATH):
        if not os.path.exists(os.path.join(data_path, dataset)):
            os.makedirs(os.path.join(data_path, dataset))
        try:
            download_data(dataset, data_path)
            self.load_from_folder(os.path.join(data_path, dataset))
        except Exception as e:
            print(e)

if __name__ == '__main__':
    phen_db = PhenotypicDatabase()
    phen_db.load_default("rao-2018")
    print(phen_db.generate_dataframe().head)