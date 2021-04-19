import os
import re
import pickle
import pandas as pd
from typing import Dict, List

from rarecrowds.utils.mondo import Mondo
from rarecrowds.utils.hpoa import Hpoa
from rarecrowds.utils.orpha import Orpha


class PhenAnnotations:
    """Load disease annotation data from multiple sources."""

    def __init__(self, reload_orpha=False, reload_mondo=False, reload_hpoa=False):
        """
        Load disease annotation data.
        If filepath is not provided, load pickle data.
        Alternatively, load HPOA data file (tsv).
        """
        orpha = Orpha(reload_orpha)
        # hpoa = Hpoa(reload_hpoa) # NOT USED
        # mondo = Mondo(reload_mondo)  # NOT USED
        # self.data = self.__getData()
        self.data = orpha.data

    def __getitem__(self, disease: str) -> List[str]:
        """Get disease data."""
        try:
            return self.data[disease.upper()]
        except:
            return None

    def getDisease(self, disease: str) -> List[str]:
        """Get disease data."""
        try:
            return self.data[disease.upper()]
        except:
            return None

    def getPhenotype(self, disease: str) -> List[str]:
        """Get disease phenotype object."""
        try:
            return self.data[disease.upper()]["phenotype"]
        except:
            return None

    def getOnset(self, disease: str) -> List[str]:
        """Get disease age information."""
        try:
            return self.data[disease.upper()]["ageOnset"]
        except:
            return None

    def getPrevalence(self, disease: str) -> List[str]:
        """Get disease prevalence information."""
        try:
            return self.data[disease.upper()]["prevalence"]
        except:
            return None
