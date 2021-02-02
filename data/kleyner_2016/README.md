# Kleyner et al. 2016

This directory contains the data found in the supplemental materials of [Kleyner et al.](http://molecularcasestudies.cshlp.org/content/2/6/a001131.long).

## Phenotype data
The phenotype data is found in any of the `tsv` files. This format is not ideal, it was simply used to be consistent with the data stored from Rao et al.

## VCF data
A pedigree file was added after importing the data. In order to analyze this by the Exomiser, the VCF files need to be merged into a multisample VCF file. This has not been done yet. A PED file has been added.

Each file's proband column was modified with the following commands:
```
for f in *.vcf; do
    fshort=${f/.vcf/}
    sed -i "s:FORMAT\tNA:FORMAT\t${fshort}:" $f
    bgzip $f
done
```

This command requires bgzip. If it is not available, install in Ubuntu with `sudo apt-get install -y tabix`.
