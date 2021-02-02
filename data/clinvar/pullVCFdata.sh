#!/bin/bash

datadir="data"
cd ${datadir}
## Get data from ClinVar
src="https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"
ver="https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.md5"
src_name="clinvar.vcf.gz"
ver_name="clinvar.vcf.gz.md5"
temp_ver="new_version.md5"

outfile="clinvar_with_hpo.vcf"

echo "Getting new MD5 version file..."
wget ${ver} -O ${temp_ver} &>/dev/null
if [ -s ${ver_name} ] && cmp -s "${ver_name}" "${temp_ver}"; then
    echo 'Already newest ClinVar version. No need to update.'
    rm ${temp_ver}
else
    echo 'There is a new ClinVar version. Updating...'
    wget ${src} -O ${src_name} && wget ${src_tbi} -O ${src_tbi_name}
    if [ $? -eq 0 ]; then
        mv ${temp_ver} ${ver_name}
    fi
    ## Unzip and select only header+lines with HP terms.
    echo 'Subsetting...'
    gunzip -f ${src_name}
    grep -E "(^#|HP:[0-9][0-9][0-9][0-9][0-9][0-9][0-9])" ${src_name/.gz/} > ${outfile}
    gzip -f ${outfile}
    rm ${src_name}
fi
