# RareCrowds
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Package to serve public data from rare disease patients as found in publications and public resources. Most cases here collected have only phenotypic data as a list of HPO terms.

## TODOs:

Ideally this repository is converted into a module that can be installed through pip/conda. For this to happen this needs to be done:
- Define a common data format: Phenopacket.
- Transform the available data into lists of Phenopackets.
- Define structure to serve available data (ideally with a similar interface to HuggingFace).
- Create all other required files (like setup.py)
- Later on:
  - Improve data ingestion pipelines.
  - Make sure that no patient is included twice -> identity!

## Available data

Data will include:

| Publication | Edited | Source | N. cases | Genetic data |
|-------------|--------|--------|----------|--------|
| [Stavropoulos, 2016](https://dx.doi.org/10.1038/npjgenmed.2015.12) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 28 | No |
| [Bone, 2016](https://dx.doi.org/10.1038/gim.2015.137) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 3 | No |
| [Stelzer, 2016](https://dx.doi.org/10.1186/s12864-016-2722-2) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 2 | No |
| [Lee, 2016](https://dx.doi.org/10.1001/jama.2014.14604) | No | [Rao, 2018](https://pubmed.ncbi.nlm.nih.gov/29980210/) | 200 | No |
| [Kleyner, 2016](http://molecularcasestudies.cshlp.org/content/2/6/a001131.long) | Yes | [Kleyner, 2016](http://molecularcasestudies.cshlp.org/content/2/6/a001131.long) | 1 | VCF file |
| [Zemojtel, 2014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4512639) | No | [Supp.](https://stm.sciencemag.org/content/scitransmed/suppl/2014/08/29/6.252.252ra123.DC1/6-252ra123_SM.pdf) | 11 | No |
| [Cipriani, 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7230372/) | No | [Supp.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7230372/bin/genes-11-00460-s001.pdf) | 134 | No |
| [Tomar, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6777628/) | No | [Supp.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6777628/bin/41431_2019_412_MOESM2_ESM.docx) | 50 | No |
| [Ebiki, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6739250/) | No | [Supp.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6739250/bin/yam-62-244-s002.pdf) | 20 | No |
| [ClinVar](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz) | Subsampled | [ClinVar](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz) | ?? | Single variants |
Total cases: 449 + clinvar

### Stavropoulos, 2016
### Bone, 2016
### Stelzer, 2016
### Lee, 2016
### Kleyner, 2016
### Zemojtel, 2014
### Cipriani, 2020
### Tomar, 2020
### Ebiki, 2019
### ClinVar

## References
Most references are provided in the table above.

![NCBI logo required by ClinVar](resources/NCBI_powered.png "NCBI logo required by ClinVar")