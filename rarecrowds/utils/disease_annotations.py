import os
import re
import pickle
import pandas as pd
from typing import Dict, List

from rarecrowds.utils.mondo import Mondo
from rarecrowds.utils.hpoa import Hpoa
from rarecrowds.utils.orpha import Orpha

class PhenAnnotations():
    '''Load disease annotation data from multiple sources.'''
    def __init__(self, mode='intersect', reload_orpha=False, reload_mondo=False, reload_hpoa=False):
        '''
        Load disease annotation data.
        If filepath is not provided, load pickle data.
        Alternatively, load HPOA data file (tsv).
        '''
        orpha = Orpha(reload=reload_orpha)
        hpoa = Hpoa(reload=reload_hpoa)
        mondo = Mondo(update=reload_mondo)  # Used to link Orpha and OMIM
        if mode == 'intersect':
            self.data = self.__getIntersection(orpha, hpoa, mondo)
        elif mode == 'orpha':
            self.data = orpha.data
        elif mode == 'hpoa':
            self.data == hpoa.data
    
    def __getIntersection(self, orpha, hpoa, mondo):
        '''
        The intersection simply selects Orphanet's symptoms that are also present in OMIM.
        The frequency, sex, onset and modifiers data needs to be merged still.
        '''
        # Only orpha diseases with symptoms annotated by OMIM
        data = {}
        for i,(orphaid,orphadis) in enumerate(orpha.data.items()):
            tempid = 'Orphanet:'+orphaid.split(':')[1]
            mondo_id = mondo.mapping.get(tempid, '')
            xrefs = mondo.xrefs.get(mondo_id, [])
            omims = [i for i in xrefs if 'OMIM' in i.upper()]
            if omims:
                # print(orphaid, orphadis['phenotype'])
                data[orphaid] = orphadis
                omim_phen = {}
                for omimid in omims:
                    # GET PHENOTYPE DATA
                    # print(omimid, hpoa.data[omimid]['phenotype'])
                    if omimid in hpoa.data:
                        for hpid,hpval in hpoa.data[omimid]['phenotype'].items():
                            # Add symptom if not present
                            if not hpid in omim_phen:
                                omim_phen[hpid] = hpval
                            else:
                                # Add phenotype attributes as items to list
                                # Possible attrbs: 'frequency', 'modifier', 'onset', 'sex'
                                for key,val in hpval.items():
                                    if key in omim_phen[hpid]:
                                        if type(omim_phen[hpid]) != list:
                                            omim_phen[hpid][key] = list(
                                                omim_phen[hpid][key])
                                        else:
                                            omim_phen[hpid][key].append(val)
                                            if type(val) == list:
                                                print('Appending list!!')
                                                print(omim_phen[hpid][key])
                                                print(val)
                ## REMOVE SYMPTOMS NOT PRESENT IN OMIM DISEASES
                if data[orphaid].get('phenotype'):
                    for k in list(data[orphaid].get('phenotype')):
                        if k not in omim_phen:
                            # print('removing:', k)
                            del data[orphaid]['phenotype'][k]
            # ADD INHERITANCE DATA
            # for hpid, hpval in hpoa.data[omimid]['phenotype']:
            # if omims:
            #     print(orphaid, orphadis)
            #     print(omims)
            #     if i > 1:
            #         break


        return hpoa.data

    def __getitem__(self, disease: str) -> List[str]:
        '''Get disease data.'''
        try:
            return self.data[disease.upper()]
        except:
            return None
    
    def getDisease(self, disease: str) -> List[str]:
        '''Get disease data.'''
        try:
            return self.data[disease.upper()]
        except:
            return None
    
    def getPhenotype(self, disease: str) -> List[str]:
        '''Get disease phenotype object.'''
        try:
            return self.data[disease.upper()]['phenotype']
        except:
            return None
    
    def getOnset(self, disease: str) -> List[str]:
        '''Get disease age information.'''
        try:
            return self.data[disease.upper()]['ageOnset']
        except:
            return None
    
    def getPrevalence(self, disease: str) -> List[str]:
        '''Get disease prevalence information.'''
        try:
            return self.data[disease.upper()]['prevalence']
        except:
            return None
