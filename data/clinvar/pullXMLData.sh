#!/bin/bash

## Get data from ClinVar
src="https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/ClinVarFullRelease_00-latest.xml.gz"
src_name="ClinVarFullRelease_00-latest.xml.gz"
ver="https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/ClinVarFullRelease_00-latest.xml.gz.md5"
ver_name="ClinVarFullRelease_00-latest.xml.gz.md5"
temp_ver="new_version.md5"

echo "Getting new MD5 version file..."
wget -c ${ver} -O ${temp_ver} &>/dev/null
if [ -s ${ver_name} ] && cmp -s "${ver_name}" "${temp_ver}"; then
    echo 'Already newest ClinVar version. No need to update.'
    rm ${temp_ver}
else
    printf 'There is a new ClinVar version. Updating...' "$file1" "$file2"
    wget ${src} && gunzip -f ${src_name}
    if [ $? -eq 0 ]; then
        mv ${temp_ver} ${ver_name}
    fi
fi
