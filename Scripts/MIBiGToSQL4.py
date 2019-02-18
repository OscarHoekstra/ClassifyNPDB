#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Takes all entries from the MIBiG repository and adds them
to a new table in the local NPDB SQL database. Also adds Inchi-keys
created by RDKit.
"""

import sqlite3
import time
import sys
import requests
import json
from Scripts import InteractWithSQL, ClassifyMibigTsv
from rdkit import Chem

def JoinList(LIST):
    """Joins a list to form a string, if the input is a list.
    Otherwise the input is likely already a string and can be returned"""
    if type(LIST) == list:
        out = ', '.join(LIST)
    elif type(LIST) == str:
        out = LIST
    return out

def CreateRDKitSmile(smile,doKekulize,dokekuleSmiles,doisomericSmiles):
    """Takes a smile string and tries to translate it with RDKit to a
    new smile with the other settings mentioned in the arguments set to
    True or False.
    See rdkit.Chem package for further explanation.
    """
    if smile == "NA":
        RDKITsmile = smile
    else:
        m = Chem.MolFromSmiles(smile)
        if doKekulize == True:
            Chem.Kekulize(m)
        RDKITsmile = (Chem.MolToSmiles(m,kekuleSmiles=dokekuleSmiles,isomericSmiles=doisomericSmiles),)[0]
    return RDKITsmile

def CreateRDKitInchiKey(smile):
    """Translates a smile string to an Inchi-key with RDKit.
    See rdkit.Chem package for further explanation.
    """
    if smile == "NA":
        inchi_key = "NA"
        return inchi_key
    else:
        m = Chem.MolFromSmiles(smile)
        inchi_key = Chem.inchi.MolToInchiKey(m)
    return inchi_key

def GetSubclass(GP):
    """Accepts the general paramameters list of a MIBiG JSON file and
    returns a list of biosynthetic-subclasses that are in it.
    """
    OutList = []
    for Type in GP['biosyn_class']:
        if Type == "NRP":
            OutList.append(Type+": "+GP.get(Type,{}).get('subclass','NA'))
        elif Type == "Polyketide":
            OutList.append(Type+": "+GP.get(Type,{}).get('pk_subclass','NA'))
        elif Type == "RiPP":
            OutList.append(Type+": "+GP.get(Type,{}).get('ripp_subclass','NA'))
        elif Type == "Terpene":
            OutList.append(Type+": "+GP.get(Type,{}).get('terpene_subclass','NA'))
        elif Type == "Saccharide":
            OutList.append(Type+": "+GP.get(Type,{}).get('saccharide_subclass','NA'))
        elif Type == "Alkaloid":
            OutList.append(Type+": "+GP.get(Type,{}).get('alkaloid_subclass','NA'))
        elif Type == "Other":
            OutList.append(Type+": "+GP.get(Type,{}).get('other_subclass','NA'))
        else:
            if GP.get('Other') != None:
                OutList.append('Other'+": "+GP['Other'].get('other_subclass','NA'))
            else:
                print("You shouldnt be able to get here!")
                print("There seems to be a biosynthetic class that was not correct")
                exit(1)
    if len(OutList) == 0:
        return ["NA"]
    else:
        return OutList

def main(sqlite_file, table_name, CompoundDict = None, FailMax = 10):
    """Creates a new table in a SQlite file to add the MIBiG data to.
    Keyword Argument:
        SqliteFile -- Path of the SQlite database to add the MIBiG data to
        MIBiGtableName -- Name of the to be created or edited table
        CompoundDict -- Dictionary with compound ids+names as keys and
                        smiles as values.
        FailMax -- How many structures in a row should be missing before it
                   assumes it is at the end of the BGCs
    """
    StartTime = time.time()
    id_column = 'compound_id' # name of the column with the primary key
    # names of the new columns
    column_names = ['compound_name','biosyn_class','biosyn_subclass',\
    'chem_synonyms','chem_target','molecular_formula','mol_mass',\
    'chem_struct','pubchem_id','chemspider_id','chebi_id','chembl_id',\
    'chem_act','other_chem_act','loci','publications','rdkit_smile_1',\
    'rdkit_smile_2','rdkit_smile_3','rdkit_smile_4','rdkit_inchi_key',\
    'rdkit_inchi_key1']
    column_type = 'TEXT'

# Connecting to the database file
    conn = sqlite3.connect(sqlite_file) # Connecting to the database
    c = conn.cursor() # Adding a cursor to interact with the database

# Adding new table or new columns, if they do not exist yet,
# without a row value.
    InteractWithSQL.CreateNewTable(c,table_name,id_column,column_names,column_type)

#Adding the usefull MIBiG data to the specified SQlite Database
# in a (new) table named 'mibig'
    BGCnr = 1 # initiate counter for checking if BGCs exits.
    FailCounter = 0 # counter for how many BGCs in a row are missing
    FailedBGCs = [] # initalising a list to store BGC that have failed
    QueryDict = {} # initialise a dictionary with which the SQL filling
                   # command will be constructed

    while FailCounter < FailMax: # while not at the end of the database
        try:
            # Create the BGC id which always has 7 numbers
            BGC = "BGC"+str(BGCnr).zfill(7)
            url = "https://mibig.secondarymetabolites.org/repository/"+BGC+"/"+BGC+".json"
            r = requests.get(url) # Load the json of the current BGC
            JsonDict = r.json() # Translate the json to a dictionary.
            CompoundInJson = 0 # Counter to find out how many compounds are in a BGC
            # For each compound in each json/dict
            for compound in JsonDict['general_params']['compounds']:
                # If one of the jsons is formatted incorrectly or is missing
                # a crucial value we do not want the whole script to error.
                try:
                    GP = JsonDict['general_params']
                    MIBIGaccession = GP['mibig_accession']
                    CompoundName = compound.get('compound','NA')
                    try:
                        if CompoundDict == None:
                            ChemStruct = compound.get('chem_struct','NA')
                        else:
                            ChemStruct = CompoundDict[MIBIGaccession+'_'+CompoundName]
                    except KeyError as e:
                        ChemStruct = 'NA'
                except Exception as e:
                    print("Error occured at the first step of:")
                    print(BGC)
                    #print(EX)
                    print(e)

                # Split up because it simplified the changing of ChemStruct
                try:
                    QueryDict['compound_id'] = MIBIGaccession+"_"+str(CompoundInJson)
                    QueryDict['compound_name'] = CompoundName
                    QueryDict['biosyn_class'] = JoinList(GP['biosyn_class'])#List
                    QueryDict['biosyn_subclass'] = JoinList(GetSubclass(GP))#List
                    QueryDict['chem_synonyms'] = JoinList(compound.get('chem_synonyms','NA'))#List
                    QueryDict['chem_target'] = compound.get('chem_target','NA')
                    QueryDict['molecular_formula'] = compound.get('molecular_formula','NA')
                    QueryDict['mol_mass'] = compound.get('mol_mass','NA')
                    QueryDict['chem_struct'] = ChemStruct
                    QueryDict['pubchem_id'] = compound.get('pubchem_id',"NA")
                    QueryDict['chemspider_id'] = compound.get('chemspider_id',"NA")
                    QueryDict['chebi_id'] = compound.get('chebi_id',"NA")
                    QueryDict['chembl_id'] = compound.get('chembl_id',"NA")
                    QueryDict['chem_act'] = JoinList(compound.get('chem_act','NA'))#List
                    QueryDict['other_chem_act'] = compound.get('other_chem_act','NA')
                    QueryDict['loci'] = GP['loci'].get('complete',"NA")
                    QueryDict['publications'] = JoinList(GP.get('publications','NA'))
                    QueryDict['rdkit_smile_1'] = CreateRDKitSmile(ChemStruct,False,False,False)
                    QueryDict['rdkit_smile_2'] = CreateRDKitSmile(ChemStruct,True,False,False)
                    QueryDict['rdkit_smile_3'] = CreateRDKitSmile(ChemStruct,False,True,False)
                    QueryDict['rdkit_smile_4'] = CreateRDKitSmile(ChemStruct,True,True,False)
                    QueryDict['rdkit_inchi_key'] = CreateRDKitInchiKey(QueryDict['rdkit_smile_1'])
                    QueryDict['rdkit_inchi_key1'] = QueryDict['rdkit_inchi_key'][0:14]


                    QueryDict = {k: "NA" if v == "" else v for k, v in QueryDict.items()}
                    FailCounter = 0
                # print which compound was wrong
                except Exception as e:
                    print("Error occured at the second step of:")
                    print(BGC)
                    print(e)
                InteractWithSQL.InsertOrUpdate(c,table_name,QueryDict)
                CompoundInJson += 1
        except json.JSONDecodeError:
            FailCounter += 1
            FailedBGCs.append(BGC)
        if FailCounter == FailMax:
            print("Stopped at: "+BGC+" because the last "+str(FailMax)+" BGCs have not been found.")
            print("You should probably check if this is past the latests BGC")
        BGCnr += 1 # go to next BGC
        if (BGCnr - 1) % 200 == 0:
            print("Arrived at "+BGC)

    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

    # Print which BGC have failed to load, because they either are not
    # available or an error with the page has occured.
    print("The BGC that have failed to load are:")
    print(', '.join(FailedBGCs))
    return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Needed argument: SQlite database, MIBiG table name, MIBiG smiles tsv file")
        exit(0)
    StartTime = time.time()
    MibigCompoundDict = ClassifyMibigTsv.LoadMibigTsv(sys.argv[3])
    main(sys.argv[1], sys.argv[2],MibigCompoundDict)
    EndTime = time.time()
    print("MIBiGToSQL4 has finished!")
    if EndTime-StartTime < 300:
        print("Running MIBiGToSQL4 took "+\
         str(round(EndTime-StartTime))+" Seconds")
    else:
        print("Running MIBiGToSQL4 took "+\
         str(round((EndTime-StartTime)/60))+" Minutes")
