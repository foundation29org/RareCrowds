# RareCrowds
[![Build Status](https://travis-ci.com/foundation29org/RareCrowds.svg?branch=main)](https://travis-ci.com/foundation29org/RareCrowds) ![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Package to serve public data from rare disease patients as found in publications and public resources. Most cases here collected have only phenotypic data as a list of HPO terms. The package offers 5 core modules:
- [DiseaseAnnotations](#diseaseannotations): Disease information.
- [HPO](#hpo): Symptom analysis through HPO.
- [PatientSampler](#patientsampler): Functionality to sample simulated patients based on the disease annotations and HPO.
- [PhenotypicComparison](#phenotypiccomparison): Functionality to plot phenotypic comparisons between two phenotypic profiles.
- [PhenotypicDatabase](#phenotypicdatabase): Local database to push available data to and pull data from. Publicly available data will be persisted here.

The 5 modules are covered in the [Usage section](#usage) below.

This package is in early development, so do not expect to see extense docstrings and sphinx documentation. At this point, this README is your best resource. Any doubt, please create an Issue and we'll give you an answer ASAP.

## Installation
To install it simply run:
`pip install rarecrowds`

The PyPI project lives here: https://pypi.org/project/rarecrowds/.

## Usage

### DiseaseAnnotations
Disease information is extracted from Orphanet's orphadata ([product 4](http://www.orphadata.org/data/xml/en_product4.xml), [product 9 (prevalence)](http://www.orphadata.org/data/xml/en_product9_prev.xml) and [product 9 (ages)](http://www.orphadata.org/data/xml/en_product9_ages.xml)) and from the [HPOA file](http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa) created by the Monarch Initiative within the HPO project. By default, Orphanet's and OMIM phenotypic description of a rare disease are intersected.

In order to get information from a particular disease, use the following lines:
```python
from rarecrowds import DiseaseAnnotations
dann = DiseaseAnnotations(mode='intersect')
data = dann.data['ORPHA:324']
```
This will output the information available about Fabry disease, with Orphanet's ID `ORPHA:324`. In order to query the disease information, please use Orphanet IDs. For further reference, visit [www.orpha.net](www.orpha.net).

The following is an extract of the data returned by the lines above:
```python
data = {
    'ageDeath': ['adult'],
    'ageOnset': ['Childhood'],
    'group': 'Disorder',
    'inheritance': ['X-linked recessive'],
    'link': 'http://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert=324',
    'name': 'Fabry disease',
    'phenotype': {   'HP:0000083': {   'frequency': 'HP:0040281',
                                       'modifier': {   'diagnosticCriteria': True}},
                     'HP:0000091': {   'frequency': 'HP:0040282',
                                       'modifier': {   'diagnosticCriteria': True}},
                     ## Many other symptoms here
                     'HP:0100820': {   'frequency': 'HP:0040283',
                                       'modifier': {   'diagnosticCriteria': True}}},
    'prevalence': [   {   'class': '1-9 / 1 000 000',
                          'geographic': 'Europe',
                          'meanPrev': '0.22',
                          'qualification': 'Value and class',
                          'source': 'ORPHANET',
                          'type': 'Prevalence at birth',
                          'validation': {'status': 'Not yet validated'}},
                      ## Other prevalence studies here
                      {   'class': '1-9 / 100 000',
                          'geographic': 'Sweden',
                          'meanPrev': '1.11',
                          'qualification': 'Value and class',
                          'source': '25274184[PMID]',
                          'type': 'Prevalence at birth',
                          'validation': {'status': 'Validated'}}],
    'source': {},
    'type': 'Disease',
    'validation': {'date': '2016-06-01 00:00:00.0', 'status': 'y'}
}
```

Based on this data, one may subset the diseases in order to get a list of diseases of interest recommended at the beginning of the development of a phenotypic analysis algorithm:
```python
phen = PhenAnnotations()
ann = phen.data
del phen
print(f'# total initial entities: {len(ann)}')
## Keep only disorders
for dis,val in list(ann.items()):
    if val['group'] != 'Disorder':
        del ann[dis]
print(f'# disases: {len(ann)}')
## Keep only those with phenotypic information
for dis,val in list(ann.items()):
    if not val.get('phenotype'):
        del ann[dis]
print(f'# disases with phenotype data: {len(ann)}')
## Remove clinial syndromes
for dis,val in list(ann.items()):
    if val['type'].lower() == 'clinical syndrome':
        del ann[dis]
print(f'# diseases w/o clinical syndromes: {len(ann)}')
## Keep only selected prevalences
valid_prev = ['>1 / 1000', '6-9 / 10 000', '1-5 / 10 000', '1-9 / 100 000', 'Unknown', 'Not yet documented']
for dis, val in list(ann.items()):
    if 'prevalence' in val:
        classes = [a['class'] for a in val['prevalence'] if a['type'] == 'Point prevalence']
        if not any(x in valid_prev for x in classes):
            del ann[dis]
    else:
        del ann[dis]
print(f'# disases with valid prevalence: {len(ann)}')
```

As a result, the number of entities in the disease annotations object should be reduced as follows:
```python
# total initial entities: 6930
# disases: 5745
# disases with phenotypes: 3649
# diseases w/o clinical syndromes: 3628
# disases with valid prevalence: 1288
```

### HPO
Symptoms are organized through the [Human Phenotype Ontology (HPO)](https://hpo.jax.org/). If you are not familiar with it, please visit the website.

In order to get information on specific symptom IDs and other items included in the HPO ontology, such as the frequency subontology, RareCrowds includes the HPO module.

In order to get information about a specific HPO term, run the following lines:
```python
from rarecrowds import Hpo
hpo = Hpo()
hpo['HP:0001250'] ## Get information about 'seizures'
```
In order to see the successors or predecessors of a particular term, run any of the following lines:
```python
hpo.successors(['HP:0001250'])
hpo.predecessors(['HP:0001250'])
```
In order to simplify a phenotypic profile, leaving only most informative, yet independent, terms run the following lines:
```python
hpo.simplify(['HP:0001250', 'HP:0007359'])
```

### PatientSampler
This module allows the creation of realistic patient profiles based on the disease annotations. The following steps are followed to sample a patient from a given disease:
1. Sample symptoms using the symptom frequency.
2. From the selected symptoms, sample imprecision as a Poisson process with a certain probability of getting a less specific term using the HPO ontology.
3. Add random noise sampling random HPO terms. The amount of random noise is also a Poisson process, while the selection of the HPO terms to include is uniform across the phenotypic abnormality subontology (disregarding too uninformative terms).

In order to sample 5 patients from a disease, run the following lines:
```python
from rarecrowds import PatientSampler
sampler = PatientSampler()
patients = sampler.sample(['ORPHA:324'], 5)
```

As a result, an object similar to the following would be generated:
```python
patients = {
    'ORPHA:324': {
        'id': 'ORPHA:324',
        'name': 'Fabry disease',
        'phenotype': {
            'HP:0000083': {'Frequency': 'HP:0040281'},
            ## Many other symptoms here
            'HP:0100820': {'Frequency': 'HP:0040283'}},
        'cohort': [ # As many items in the list as patients simulated
            {
                'ageOnset': None,
                'phenotype': {
                    'HP:0025031': {},
                    ## Other symptoms here
                    'HP:0100279': {}
                }
            }
        ]
    }
}
```

You can configure the imprecision and noise levels used to sample patient symptoms:
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

### PhenotypicComparison
Comparing phenotypic profiles is often tricky. Venn diagrams are helpful, but often fall short in cases with complicated symptom relations. This module offers a detailed view of the overlap between, at most, 2 phenotypic profiles. It plots the HPO ontology graph with nodes color coded marking the common nodes and the nodes belonging to each profile. The plots use Plotly, so an interactivity-enabled viewer is recommended (most notebooks support this).

If a single phenotypic profile is passed as argument, it will plot the symptoms:
```python
from rarecrowds import PhenotypicComparison
PhenotypicComparison.plot(
    patient = patients['ORPHA:324']['cohort'][0]['phenotype'],
    disease = {
        'name': patients['ORPHA:324']['name'],
        'id': patients['ORPHA:324']['id'],
        'phenotype': patients['ORPHA:324']['phenotype']})
```
![Showing a phenotypic profile](https://github.com/foundation29org/RareCrowds/blob/main/resources/profile.png)

If two phenotypic profiles are passed as argument, it will plot a comparison:
```python
PhenotypicComparison.plot(
    patient = patients['ORPHA:324']['cohort'][0]['phenotype'],
    disease = { # This entry may also be a list of HPO terms.
        'name': patients['ORPHA:324']['name'],
        'id': patients['ORPHA:324']['id'],
        'phenotype': patients['ORPHA:324']['phenotype']})
```
![Comparing two phenotypic profiles](https://github.com/foundation29org/RareCrowds/blob/main/resources/profile_comparison.png)

### PhenotypicDatabase
Finally, you may use the PhenotypicDatabase module to pull data from public sources. Currently, there are the supported sources:

| Publication | Edited | Source | N. cases |
|-------------|--------|--------|----------|
| [Stavropoulos, 2016](https://dx.doi.org/10.1038/npjgenmed.2015.12) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 28 |
| [Bone, 2016](https://dx.doi.org/10.1038/gim.2015.137) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 3 |
| [Stelzer, 2016](https://dx.doi.org/10.1186/s12864-016-2722-2) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 2 |
| [Lee, 2016](https://dx.doi.org/10.1001/jama.2014.14604) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 200 |
| [Kleyner, 2016](http://molecularcasestudies.cshlp.org/content/2/6/a001131.long) | Yes | [Kleyner, 2016](http://molecularcasestudies.cshlp.org/content/2/6/a001131.long) | 1 |
| [Zemojtel, 2014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4512639) | No | [Supp.](https://stm.sciencemag.org/content/scitransmed/suppl/2014/08/29/6.252.252ra123.DC1/6-252ra123_SM.pdf) | 11 |
| [Cipriani, 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7230372/) | No | [Supp.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7230372/bin/genes-11-00460-s001.pdf) | 134 |
| [Tomar, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6777628/) | No | [Supp.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6777628/bin/41431_2019_412_MOESM2_ESM.docx) | 50 |
| [Ebiki, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6739250/) | No | [Supp.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6739250/bin/yam-62-244-s002.pdf) | 20 |
| [ClinVar](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz) | Subsampled | [ClinVar](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz) | 68153 |

To get an instance of the `PhenotypicDatabase`:
```python
from rarecrowds import rarecrowds
db = rarecrowds.PhenotypicDatabase()
```

The PhenotypicDatabase instance manages your local database. You may add data to it by downloading available data or by generating it locally (via simulations or a local push). Available datasets are not in your local database until you explicitly download them. To check what datasets are available and load them for later usage run:
```python
datasets = db.get_available_datasets()
db.load('some_dataset')
```

In order to dump data from your database, you can get either a pandas dataframe or a list of dictionaries. To get a dataframe of the data in the database:
```python
df = db.generate_dataframe()
```

To get a list of dictionaries of the data in the database:
```python
data = db.generate_list_of_dicts()
```

# References and attributions
The following references and attributions need to be added:

TODO: Add them
