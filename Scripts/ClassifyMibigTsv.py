#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Loads a TSV file with mibig compound-id, compound name and
smile strings, uploads the smiles to ClassyFire and creates a dictionary
with the compound id and name with the QueryID to retrieve the
classification later.
"""
import sys
from Scripts import Run_pyclassyfire4
import pickle

def LoadMibigTsv(InFile):
    """ Loads a tsv file with all smiles available for the mibig dataset and
    saves the mibig accession and compound-name as CompoundID and the smile
    as Structure in a dictionary CompoundDict
    """
    CompoundDict = {}
    with open(InFile, 'r') as f:
        f.readline()
        File = f.readlines()
    for line in File:
        line = line.split('\t')
        CompoundID = line[0]+"_"+line[1]
        Structure = line[2]
        if CompoundID in CompoundDict:
            print('THIS SHOULD NOT HAPPEN,',
            'There seems to be a duplicate in the mibig smile tsv file,',
            'Check the file for errors!')
            print(CompoundID)
            exit(1)
        if len(Structure) > 0:
            CompoundDict[CompoundID] = Structure
    return CompoundDict


def main(InFile):
    # Create a dictionary with the mibig compounds and smiles.
    CompoundDict = LoadMibigTsv(InFile)

    QueryIDDict = Run_pyclassyfire4.PyClassifyStructureList(CompoundDict)
    with open("PickledQueryIDDict.txt",'wb') as f:
        pickle.dump(QueryIDDict, f)
        print("Saved PickledQueryIDDict")
    #Run_pyclassyfire4.GetPyclassyfireResults(QueryIDDict)



if __name__ == "__main__":
    InFile = sys.argv[1]
    main(InFile)


    print("Done")
