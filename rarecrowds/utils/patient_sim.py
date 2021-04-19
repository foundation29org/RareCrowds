from datetime import datetime
import numpy as np
from typing import Dict, List
import uuid

from rarecrowds.utils.disease_annotations import PhenAnnotations
from rarecrowds.utils.hpo import Hpo


def build_eligibles(phen_data, hpo_data) -> List[str]:
    items = set()
    for disease in phen_data.values():
        for hp in disease.get("phenotype", {}).keys():
            items.add(hp)
            for ancestor in hpo_data.predecessors(hp, depth=1):
                items.add(ancestor)
    items = list(items)
    items.sort()
    return items


class PatientSampler:
    def __init__(self):
        """
        Class to sample rare disease patients.
        """
        self.__poisson_lambda = 1
        self.__noise_ratio = 0.25
        self.__random_generator = np.random.default_rng()
        self.__dx_criteria_frequency = "Very frequent"
        self.__default_frequency = ["HP:0040282", "HP:0040283"]

        self.__frequency_by_id = {
            "HP:0040280": {"name": "obligate", "interval": [1.00, 1.00]},
            "HP:0040281": {"name": "very frequent", "interval": [0.80, 0.99]},
            "HP:0040282": {"name": "frequent", "interval": [0.30, 0.79]},
            "HP:0040283": {"name": "occasional", "interval": [0.05, 0.29]},
            "HP:0040284": {"name": "very rare", "interval": [0.01, 0.04]},
            "HP:0040285": {"name": "excluded", "interval": [0, 0]},
        }
        self.__frequency_by_name = {
            "obligate": {"id": "HP:0040280", "interval": [1.00, 1.00]},
            "very frequent": {"id": "HP:0040281", "interval": [0.80, 0.99]},
            "frequent": {"id": "HP:0040282", "interval": [0.30, 0.79]},
            "occasional": {"id": "HP:0040283", "interval": [0.05, 0.29]},
            "very rare": {"id": "HP:0040284", "interval": [0.01, 0.04]},
            "excluded": {"id": "HP:0040285", "interval": [0, 0]},
        }
        self.cases = {
            "default": {
                "imprecision": 1,
                "noise": 0.25,
                "omit_frequency": False,
            },
            "ideal": {
                "imprecision": 0,
                "noise": 0,
                "omit_frequency": True,
            },  # For debugging. No noise. All patients = disease.
            "freqs": {
                "imprecision": 0,
                "noise": 0,
                "omit_frequency": False,
            },  # For simple cases without noise. All patients = disease*frequencies.
            "impre": {
                "imprecision": 1,
                "noise": 0,
                "omit_frequency": False,
            },  # Meant for patients without the most granular terms.
            "impre2": {
                "imprecision": 2,
                "noise": 0,
                "omit_frequency": False,
            },
        }
        self.phens = PhenAnnotations()
        self.hpo = Hpo()
        self.__eligibles = build_eligibles(self.phens.data, self.hpo)

    def convert_simulations_to_phenopackets(
        self, simulations: Dict, num_patients: int = 20
    ) -> List[Dict]:
        phenopacket_id_set = set()
        patient_id_set = set()
        patient_uuid_map = {}
        for i in range(num_patients):
            unique_id = uuid.uuid4().hex
            while unique_id in patient_id_set:
                unique_id = uuid.uuid4().hex
            patient_id_set.add(unique_id)
            patient_uuid_map[i] = unique_id
        phenopackets = []
        for d, data in simulations.items():
            for i in range(num_patients):
                unique_id = uuid.uuid4().hex
                while unique_id in phenopacket_id_set:
                    unique_id = uuid.uuid4().hex
                phenopacket = {}
                phenopacket["id"] = unique_id
                phenopacket["subject"] = {}
                phenopacket["subject"]["id"] = patient_uuid_map[i]
                phenopacket["phenotypicFeatures"] = []
                if data["cohort"][i]["phenotype"]:
                    for feature in data["cohort"][i]["phenotype"]:
                        phenopacket["phenotypicFeatures"].append({"type": {"id": feature}})
                phenopacket["metaData"] = {}
                phenopacket["metaData"]["submittedBy"] = "patient sampler"
                phenopacket["metaData"]["resources"] = []
                phenopacket["metaData"]["resources"].append(
                    {
                        "id": "hp",
                        "name": "human phenotype ontology",
                        "url": "http://purl.obolibrary.org/obo/hp.owl",
                        "version": "",
                        "namespacePrefix": "HP",
                        "iriPrefix": "http://purl.obolibrary.org/obo/HP_",
                    }
                )
                phenopackets.append(phenopacket)
        return phenopackets

    def sample(
        self,
        patient_params: str = "default",
        N: int = 20,
        dx_criteria_frequency: str = "Very frequent",
        default_frequency: List = ["HP:0040282", "HP:0040283"],
    ) -> Dict:
        """
        Generate N patients for each of the selected diseases.

        Dx criteria and default frequency configures what to do when frequency is unknown.
        Noise ratio represents the maximum number of HP terms that are included as noise.
        :param dx_criteria_frequency: Frequency to use with symptoms used as diagnostic criteria if frequency is unknown.
        :type dx_criteria_frequency: str
        :param default_frequency: Frequency to use when symptom frequency is unknown. If a list is passed, it will be sampled each time.
        :type default_frequency: str or list
        :param imprecision: Parameter controlling the level of imprecision. It is the lambda of a Poisson distribution. 1 means that the most granular term is as probable as the immediate predecessor. 2 means that the two predecessors are the most likely.
        :type imprecision: int
        :param noise: Ratio of noisy terms compared to patient number of phenotype terms.
        :type noise: float
        """

        if dx_criteria_frequency.lower() not in set(["obligate", "very frequent"]):
            raise ValueError(
                "dx_criteria_frequency is not 'obligate' or 'very frequent'"
            )
        self.__dx_criteria_frequency = self.__frequency_by_name[
            dx_criteria_frequency.lower()
        ]["id"]

        self.__default_frequency = default_frequency

        self.__poisson_lambda = self.cases[patient_params]["imprecision"]
        self.__noise_ratio = self.cases[patient_params]["noise"]
        self.__omit_frequency = self.cases[patient_params]["omit_frequency"]

        simulations = {}
        diseases = self.phens.data
        for d in diseases:
            try:
                disease = self.phens.data.get(d, {})
                if not disease:
                    simulations[d] = {}
                    continue
                simulations[d] = {
                    "id": d,
                    "name": disease.get("name"),
                    "phenotype": disease.get("phenotype", {}),
                    "cohort": [],
                }
                for _ in range(N):
                    simulations[d]["cohort"].append(
                        {
                            "ageOnset": self.samplePatientAge(disease.get("ageOnset")),
                            "phenotype": self.samplePatientPhenotype(
                                disease.get("phenotype")
                            ),
                        }
                    )
            except Exception as ex:
                print(d, "====================", sep="\n")
                print(disease, "====================", sep="\n")
                print(simulations[d], "====================", sep="\n")
                raise ex
        return simulations

    def samplePatientPhenotype(self, phenotype: Dict) -> List[str]:
        """
        Create new patient with configured imprecision and noise levels.
        """
        if phenotype:
            try:
                if self.__omit_frequency:
                    hpo_list = list(phenotype)
                else:
                    hpo_list = self.__sample_symptom(phenotype)
                hpo_list = self.__imprecise_hpos(hpo_list)
                hpo_list.extend(self.__random_hpos(hpo_list))
                hpos = {i: {} for i in hpo_list}
                return hpos
            except Exception as ex:
                raise ex
        else:
            return None

    def __random_hpos(self, hpos):
        """
        Sample valid HPO terms.
        The max number of terms is controlled at the class instantiation.
        A Poisson distribution is used to sample how many terms to add.
        """
        hpos = set(hpos)
        max_count = int(len(hpos) * self.__noise_ratio + 0.5)
        count = self.__random_generator.integers(
            0, max_count + 1
        )  ## upper limit is excluded
        if count > 0:
            res = list()
            while len(res) == 0 or any(x in hpos for x in res):
                res = list(self.__random_generator.choice(self.__eligibles, count))
            return res
        else:
            return []

    def __imprecise_hpos(self, hps):
        """
        Get a random ancestor following a Poisson distribution with lambda parameter
        especified in the constructor. The function may return the same input hp
        depending on the random number.
        """
        # s is the index of the ancestor to take. If s=0, the nominal is returned.
        # If s=2, the 2nd ancestor is taken.
        if self.__poisson_lambda == 0 or not hps:
            return hps
        if type(hps) == str:
            s = self.__random_generator.poisson(self.__poisson_lambda)
            if s == 0:
                return hps
            ancestors = list(self.hpo.predecessors(hps, depth=s))
            # Remove those that would be way too uninformative.
            to_remove = ["HP:0000118", "HP:0000001"]
            candidates = [i for i in ancestors if i not in to_remove]
            if not candidates:
                return hps
            return candidates[min(s - 1, len(candidates) - 1)]
        else:  ## Assuming it is a list, a set, a tuple, etc
            return [self.__imprecise_hpos(i) for i in hps]

    def __sample_symptom(self, phenotype):
        """First sample the probability from the interval, then sample the symptom using that probability."""
        l = set()
        while not l:
            for hp, data in phenotype.items():
                f = data.get("frequency")
                if not f and data.get("modifier", {}).get("diagnosticCriteria"):
                    f = self.__dx_criteria_frequency
                elif not f:
                    if type(self.__default_frequency) == str:
                        f = self.__default_frequency
                    else:
                        f = self.__random_generator.choice(self.__default_frequency)
                minf, maxf = self.__frequency_by_id[f]["interval"]
                if (
                    self.__random_generator.random()
                    < (maxf - minf) * self.__random_generator.random() + minf
                ):
                    l.add(hp)
        return list(l)

    def samplePatientAge(self, age):
        """Sample the age of a patient.
        First the onset is sampled taking only the central part of a normal distribution. If a max age is not provided, a sigma of 5 years is assumed and no hard-cap is imposed on the + side of the mode.
        Then the time of visit is sampled from a Gumbel function with a mode of 2 weeks.
        Ages from http://www.orphadata.org/cgi-bin/img/PDF/OrphadataFreeAccessProductsDescription.pdf"""

        def sampleOnset(rng, a, b=None):
            """Sample from normal distribution and keep +-sigma within interval. 10% noise is added to each side."""
            if a is None and b is None:
                return None
            onset = -10000
            noise = 0.1
            if b:
                sigma = (b - a) / 2
                mu = a + sigma
                while onset < (1 - noise) * a or onset > (1 + noise) * b:
                    onset = rng.normal(mu, sigma)
            else:
                sigma = 5  # years
                mu = a + sigma
                while onset < (1 - noise) * a:
                    onset = rng.normal(mu, sigma)
            return onset

        def sampleVisit(rng):
            """It assumes a mode of the time to visit distribution (represented by a Gumbel dist) of 2 weeks.
            Returns a time from symptom discovery to visit in years."""
            visit = -10000
            beta = 1
            mu = 2  # two weeks
            while mu + visit < 0:
                visit = rng.gumbel(mu, beta)
            return visit / (365 / 7)  # to years

        if age:
            o = Onset(age)
            # print('Final interval', age, o.min, o.max)
            onset = sampleOnset(self.__random_generator, o.min, o.max)
            if onset is None:
                return None
            visit = sampleVisit(self.__random_generator)
            return onset + visit
        else:
            return None


class Onset:
    """Onset and onset intervals in years"""

    def __init__(self, interval: str):
        if type(interval) == str:
            self.min, self.max = self.__parseStr(interval)
        elif type(interval) in [list, set, tuple] and type(interval[0]) == str:
            o = Onset(interval[0])
            for i in interval[1:]:
                o += Onset(i)
            self.min, self.max = o.min, o.max
        elif type(interval) in [list, set, tuple] and isinstance(
            interval[0], (int, float, complex)
        ):
            assert len(interval) == 2
            self.min, self.max = interval[0], interval[1]

    def __add__(self, o):
        l = [[], []]
        for i in [self, o]:
            l[0].append(i.min)
            l[1].append(i.max)
        self.min = None if None in l[0] else min(l[0])
        self.max = None if None in l[1] else max(l[1])
        return Onset([self.min, self.max])

    def __str__(self):
        return str([self.min, self.max])

    @staticmethod
    def __parseStr(age):
        age = age.lower()
        if age == "antenatal":  # Before birth
            return -6 / 12, 0
        elif age == "neonatal":  # From birth to the fourth week of life
            return 0, 1 / 12
        elif age == "infancy":  # From end of the 4th week to the 23rd month
            return 1 / 12, 2
        elif age == "childhood":  # From 2 to 11 years
            return 2, 11
        elif age == "adolescent":  # From 12 to 18 years
            return 12, 18
        elif age == "adult":  # From 19 to 65 years
            return 19, 65
        elif age == "elderly":  # After 66
            return 66, 90
        elif age == "all ages":
            return 0, 90
        elif age == "no data available":
            return None, None
        else:
            raise ValueError(f"Unknown age interval '{age}'")

