import json
import os

from google.protobuf.json_format import Parse

from rarecrowds.phenopackets_pb2 import Phenopacket


class PhenotypicDatabase:
    def __init__(self):
        self.db = {}

    def add_phenopacket(self, phenopacket: Phenopacket):
        self.db[phenopacket.id] = phenopacket

    def load_from_file(self, file_path: str) -> Phenopacket:
        with open(file_path, "r") as jsfile:
            return Parse(message=Phenopacket(), text=jsfile.read())

    def load_from_folder(self, folder_path: str):
        for file in os.listdir(folder_path):
            self.add_phenopacket(self.load_from_file(folder_path + "/" + file))
