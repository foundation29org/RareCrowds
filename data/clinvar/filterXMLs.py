#!/usr/bin/python3

import lxml.etree as lxmlET
import gzip
import argparse
import os
import sys

# Create the parser
my_parser = argparse.ArgumentParser(description='Find nodes with HPO terms in ClinVar\'s xml file.')
my_parser.add_argument('-i', '--input',
                       required=True,
                       help='The path to the input file')
my_parser.add_argument('-o', '--output',
                       required=True,
                       help='The path to the output file')
args = my_parser.parse_args()
input_path = args.input
output_path = args.output

# Check file
def check_file(f):
    if not os.path.isfile(f):
        print('The file specified does not exist')
        return False
    return True

def subset_clinvar_xml(in_path, out_path):
    root_element = 'ReleaseSet'
    element_of_interest = 'ClinVarSet'
    string_of_interest = 'HP:'
    ## Open output file's context
    with open(out_path, "wb") as fout, lxmlET.xmlfile(fout, encoding="utf-8") as xf:
        ## Get root element
        for _, elem in lxmlET.iterparse(in_path, events=('start',)):
            if elem.tag == root_element:
                attribs = elem.attrib
                break
        xf.write_declaration(standalone=True)
        ## Iterate over ClinVar sets to be stored in the ReleaseSet
        with xf.element(root_element, attribs):
            ielements = 0
            isubset = 0
            ierrors = 0
            for _, elem in lxmlET.iterparse(in_path, encoding='utf-8'):
                ielements += 1
                if elem.tag == element_of_interest:
                    try:
                        s = lxmlET.tostring(elem)
                    except lxmlET.SerialisationError:
                        ierrors += 1
                    else:
                        if string_of_interest in str(s):
                            xf.write(s, pretty_print=True)
                            isubset += 1
                            # if i > 3000000:
                            #     break
                            ## Cleanup
                            elem.clear()
                            while elem.getprevious() is not None:
                                del elem.getparent()[0]
            print('Summary of elements with HPO and total: {}/{} = {}'.format(isubset, ielements, isubset/ielements))           
            print('Errors: {}'.format(ierrors))

def process_output(filename):
    old_string1='&lt;'
    new_string1='<'
    old_string2='&gt;'
    new_string2='>'
    ## Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()

    ## Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        s = s.replace(old_string1, new_string1)
        s = s.replace(old_string2, new_string2)
        f.write(s)
    
    ## Compress output
    with open(filename, 'rb') as f_in, gzip.open(filename+'.gz', 'wb') as f_out:
        f_out.writelines(f_in)
    os.remove(filename)

if check_file(input_path):
    subset_clinvar_xml(input_path, output_path)
    process_output(output_path)
