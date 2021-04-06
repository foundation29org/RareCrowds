[![Build Status](https://travis-ci.com/foundation29org/RareCrowds.svg?branch=master)](https://travis-ci.com/foundation29org/RareCrowds)

# RareCrowds
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Package to serve public data from rare disease patients as found in publications and public resources. Most cases here collected have only phenotypic data as a list of HPO terms.

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
