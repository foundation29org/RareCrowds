[![Build Status](https://travis-ci.com/foundation29org/RareCrowds.svg?branch=master)](https://travis-ci.com/foundation29org/RareCrowds)

# RareCrowds
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Package to serve public data from rare disease patients as found in publications and public resources. Most cases here collected have only phenotypic data as a list of HPO terms.

## Installation
`pip install rarecrowds`

## Usage
To get an instance of a `PhenotypicDatabase`:
```python
from rarecrowds import rarecrowds
db = PhenotypicDatabase()
```

To check what datasets are available and download them for usage:
```python
datasets = db.get_available_datasets()
db.load_default(some_dataset)
```

To use our sampler to sample diseases for patients:
```python
'''
These are the options for patient simulation parameters
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
}
'''
          
db.load_simulated_data(patient_params="ideal", num_patients=20)
```

To get a dataframe of the data in the database:
```python
df = db.generate_dataframe()
```

To get a list of dictionaries of the data in the database:
```python
data = db.generate_list_of_dicts()
```


## TODOs:

Ideally this repository is converted into a module that can be installed through pip/conda.

For this to happen this needs to be done:
- Define a common data format: Phenopacket.
- Transform the available data into lists of Phenopackets.
- Define structure to serve available data (ideally with a similar interface to HuggingFace).
- Create all other required files (like setup.py)
- Later on:
  - Improve data ingestion pipelines.
  - Make sure that no patient is included twice -> identity!
