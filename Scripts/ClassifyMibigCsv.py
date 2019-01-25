#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Description:
"""
import sys
import Run_pyclassyfire4
import pickle

def LoadMibigCsv(InFile):
    """ Loads a tsv file with all smiles available for the mibig dataset and
    saves the mibig accession and compound-name as CompoundID and the smile\
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
            print("THIS SHOULD NOT HAPPEN, THERE SEEMS TO BE A DUPLICATE IN THE MIBIG SMILE CSV FILE")
            print(CompoundID)
            exit(1)
        if len(Structure) > 0:
            CompoundDict[CompoundID] = Structure
    return CompoundDict


def main(InFile):
    CompoundDict = LoadMibigCsv(InFile)

    QueryIDDict = Run_pyclassyfire4.PyClassifyStructureList(CompoundDict)
    with open("PickledQueryIDDict.txt",'wb') as f:
        pickle.dump(QueryIDDict, f)
        print("Saved PickledQueryIDDict")
    #Run_pyclassyfire4.GetPyclassyfireResults(QueryIDDict)



if __name__ == "__main__":
    InFile = sys.argv[1]
    main(InFile)


    print("Done")
