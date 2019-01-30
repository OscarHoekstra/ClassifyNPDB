#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: This script runs pyclassyfire on the NPDB and MIBiG SQL
database
"""
import sys
import time
import json
import sqlite3
import re
import pickle
from Scripts import GetSqlIDs, InteractWithSQL
import os
sys.path.insert(0, '/mnt/scratch/hoeks102/Thesis_Bsc/ClassyFireAPI_test')
import pyclassyfire.client

def JoinList(LIST):
    """Joins a list to form a string, if the input is a list.
    Otherwise the input is likely already a string and can be returned"""
    if type(LIST) == list:
        out = ', '.join(LIST)
    elif type(LIST) == str:
        out = LIST
    return out


def GetToClassify(RedoClassify,ToClassifyFile,NPDB_IDs):
    """Returns the list of structures that still need to be classified
    and saves a copy of the full structur_id list if you want to redo
    the classification.

    Keyword Arguments:
        RedoClassify -- boolean,
        ToClassifyFile -- Path to a file with a pickled list of still to
            be classified structure_ids
        NPDB_IDs -- Complete list of structure_ids
    """
    ToClassify = []
    if os.path.isfile(ToClassifyFile) and RedoClassify == False:
        with open(ToClassifyFile, "rb") as f:
            ToClassify = pickle.load(f)
    if RedoClassify == True: #if ToClassify.txt doesnt exist we will assume everything still has to be classified
        ToClassify = NPDB_IDs
        with open(ToClassifyFile, "wb") as f:
            pickle.dump(NPDB_IDs, f)
    return ToClassify


def FileToList(FilePath):
    """Parses a file with (space) seperated inchi-keys into a list

    Keyword Arguments:
        FilePath -- string, path to the inchi-key file
    Returns:
        List -- list, list of lists with necessary data
    """
    List = []
    with open(FilePath) as f:
        for line in f:
            List.append(line.rstrip())
    return List


def PyClassifyList(InchiList):
    """Retrieve the ClassyFire classification for a list of inchi-keys
    This is a old function I used to quickly test the quality of my
    inchi-keys as it reports how many of them got classifications.
    This hasnt got much further use because the classifications are
    not reported or saved"""
    nr_Classified = 0
    nr_Errors = 0
    print("List length: "+str(len(InchiList)))
    for i in InchiList:
        try:
            pyclassyfire.client.get_entity(i, 'json')
            nr_Classified +=1
        except:
            nr_Errors += 1
    print("Classified: "+str(nr_Classified))
    print("Errors: "+str(nr_Errors))
    return nr_Classified, nr_Errors


def TestClassyfireSpeed(FilePath):
    """Old function I used to test the time it took to retrieve the
    classification of a list of inchi-keys"""
    InchiList = FileToList(FilePath)
    StartTime = time.time()
    PyClassifyList(InchiList)
    EndTime = time.time()
    if EndTime-StartTime < 30000:
        print("Running Run_pyclassyfire.py took "+\
         str(round(EndTime-StartTime))+" Seconds")
    else:
        print("Running Run_pyclassyfire.py took "+\
         str(round(EndTime-StartTime)/60)+" Minutes")


def PyClassify(InchiKey):
    """Finds the classification of a single structures and returns
    the JSON file as a dict.

    Keyword Arguments:
        InchiKey -- string of the inchi_key of a structure
    Returns:
        JSON -- dict with classifications
    """
    ClassList = []
    try:
        JSONstring = pyclassyfire.client.get_entity(InchiKey, 'json')
        JSON = json.loads(JSONstring)
    except Exception as ex:
        #print(ex)
        UHFFInchiKey = InchiKey[0:15]+"UHFFFAOYSA"+InchiKey[25:27]
        try:
            JSONstring = pyclassyfire.client.get_entity(UHFFInchiKey, 'json')
            JSON = json.loads(JSONstring)
        except Exception as ex:
            NeutralInchiKey = InchiKey[0:26]+"N"
            try:
                JSONstring = pyclassyfire.client.get_entity(
                    NeutralInchiKey, 'json')
                JSON = json.loads(JSONstring)
            except Exception as ex:
                NeutralUHFFInchiKey = InchiKey[0:15]+"UHFFFAOYSA-N"
                try:
                    JSONstring = pyclassyfire.client.get_entity(
                        NeutralUHFFInchiKey, 'json')
                    JSON = json.loads(JSONstring)
                except Exception as ex:
                    #return False if the structure could not be classified
                    return False
    return JSON


def PyClassifyStructureList(CompoundDict):
    """Submits a smile or inchi to the ClassyFire sevice and returns
    a query id which can be used to collect results

    Keyword Arguments:
        CompoundDict -- dictionary with compound-id as key and smiles
                        or inchi as value.
    Returns:
        QueryIDDict -- dicionary with compound-id as key and the query ID
                     that can be used to retrieve ClassyFire results
                     as the value.
    """
    QueryIDDict = {}
    for key, compound in CompoundDict.items():
        try:
            QueryIDDict[key] = pyclassyfire.client.structure_query(compound)
            print(key)
            print(QueryIDDict[key])
        except Exception as e:
            print(e)
            print(key)
            print(compound)
    return QueryIDDict


def GetPyclassyfireResults(QueryIDDict):
    """Retrieve the results for a dictionary with mibig compounds and
    ClassyFire queryIDs and save the results to files.
    """
    ResultsFolder = "/mnt/scratch/hoeks102/Thesis_Bsc/mibig_classyfire_results/"
    for key, QueryID in QueryIDDict.items():
        try:
            json = pyclassyfire.client.get_results(QueryID, 'json')
            FixedCompoundID = key.replace(' ','_')
            with open(ResultsFolder+FixedCompoundID+'.json','w') as w:
                w.write(json)
        except Exception as e:
            print(e)
            print(key)
            print(QueryID)
    return None


def GetSinglePyclassyfireResult(QueryID):
    """Return the results of a ClassyFire queryID"""
    try:
        JsonString = pyclassyfire.client.get_results(QueryID, 'json')
        Class = json.loads(JsonString)
        if len(Class['entities']) > 0:
            Class = Class['entities'][0]
        else:
            Class = {}
            return False
        if 'report' in Class:
            if Class['report'] == None:
                return False
            else:
                print("If you see this, there is something wrong",
                      "with the script that needs to be fixed!")
    except Exception as e:
        print("!"*20)
        print(e)
        print(QueryID)
        print("!"*20)
        return False

    return Class


def CopyDirectParent(EX):
    """Copies the direct parent to the place it should be in the
    classificatoin hierarchy in the list EX, which will be used to
    fill the SQL database"""
    pos = 0
    for item in EX:
        if pos>0 and item == EX[0]:
            return EX
        if item == "NA":
            EX[pos] = EX[0]
            return EX
        pos += 1
    return EX


def OutputUnclassifiedStructures(ListUnclassified, ListEmpty,
                                 FailedStructures, TimeStamp):
    """Writes all the unclassified structure-IDs to a file"""
    OutFile = "UnclassifiedStructures-"+TimeStamp+".txt"
    # If no structures in the cluster failed, ignore the next part
    with open(OutFile, 'a') as w:
        for ID in ListUnclassified:
            w.write(">Unclassified\t"+ID+"\n")
        for ID in ListEmpty:
            w.write(">Empty\t"+ID+"\n")
        for ID in FailedStructures:
            w.write(">Failed\t"+ID+"\n")
    return None


def AddColumns(sqlite_file, table_name):
    """Adds the missing columns to the table of the SQL database"""
    columns = ['cf_direct_parent','cf_kingdom','cf_superclass',\
    'cf_class','cf_subclass','cf_intermediate_0','cf_intermediate_1',\
    'cf_intermediate_2','cf_intermediate_3','cf_intermediate_4',\
    'cf_intermediate_5','cf_molecular_framework','cf_alternative_parents',\
    'cf_substituents', 'cf_description']
    column_type = 'TEXT'
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file) # Connecting to the database
    c = conn.cursor() # Adding a cursor to interact with the database
    # Adding new column, if it does not exist yet, without a row value
    for new_column_name in columns:
        try:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn=table_name, cn=new_column_name, ct=column_type))
            print("Column created: {cn}".format(cn=new_column_name))
        except sqlite3.OperationalError:
            print("Column already exists: {cn}".format(cn=new_column_name))
    conn.commit()
    conn.close()
    return None


def main(IDList, SqliteFile, TableName,
         InchiColumn="inchi_key",
         Batched = False,
         TimeStamp = 000000):
    """Run Classyfire on all inchi-keys of a column in a SQlite table

    Keyword Arguments:
        IDList -- List of all IDs to find classifications from
        SqliteFile -- Path to the SQlite database
        TableName -- Name of the table in the database to edit
        InchiColumn -- Name of the column with the inchi_keys
        Batched -- Boolean, wheter to perform the classification in batches
        TimeStamp -- int/float, used to indicate when the output was created
    """
    sqlite_file = SqliteFile    # path of the sqlite database file
    table_name = TableName   # name of the table to be interacted with
    id_column = 'structure_id' # name of the PRIMARY KEY column
    inchi_column_name = InchiColumn # name of the column with the inchi_keys
    # name of the new classification column
    columns = ['cf_direct_parent','cf_kingdom','cf_superclass',\
    'cf_class','cf_subclass','cf_intermediate_0','cf_intermediate_1',\
    'cf_intermediate_2','cf_intermediate_3','cf_intermediate_4',\
    'cf_intermediate_5','cf_molecular_framework','cf_alternative_parents',\
    'cf_substituents', 'cf_description']

    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file) # Connecting to the database
    c = conn.cursor() # Adding a cursor to interact with the database

    if Batched == False:
        column_type = 'TEXT'
        # Adding new column, if it does not exist yet, without a row value
        for new_column_name in columns:
            try:
                c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                    .format(tn=table_name, cn=new_column_name, ct=column_type))
                print("Column created: {cn}".format(cn=new_column_name))
            except sqlite3.OperationalError:
                print("Column already exists: {cn}".format(cn=new_column_name))

    FailedStructures = []
    ListUnclassified = []
    ListEmpty = []
    for NP_ID in IDList:
        #print(NP_ID)
        c.execute(f"SELECT {inchi_column_name} FROM {table_name} WHERE {id_column} == '{NP_ID[0]}'")
        inchi_key = c.fetchone()[0]
        Class = PyClassify(inchi_key)
        if Class == False:
            print(inchi_key,NP_ID[0],"classification could not be found")
            EX = ["Unclassified"]*len(columns)
            ListUnclassified.append(NP_ID[0])
        elif Class == {}:
            print(inchi_key,NP_ID[0],"has an empty classification")
            EX = ["NA"]*len(columns)
            ListEmpty.append(NP_ID[0])
        elif Class != False:
            EX = []
            try:
                EX.append(Class.get('direct_parent','NA').get('name','NA'))
            except AttributeError:
                EX.append('NA')
            try:
                EX.append(Class.get('kingdom','NA').get('name','NA'))
            except AttributeError:
                EX.append('NA')
            try:
                EX.append(Class.get('superclass','NA').get('name','NA'))
            except AttributeError:
                EX.append('NA')
            try:
                EX.append(Class.get('class','NA').get('name','NA'))
            except AttributeError:
                EX.append('NA')
            try:
                EX.append(Class.get('subclass','NA').get('name','NA'))
            except AttributeError:
                EX.append('NA')
            try:
                for node in Class['intermediate_nodes']:
                    EX.append(node['name'])
            except:
                EX.append('NA')
            try:
                for i in range(6-len(Class['intermediate_nodes'])):
                    EX.append('NA')
            except:
                for i in range(6):
                    EX.append('NA')
            if Class.get('molecular_framework','NA') == None:
                EX.append("NA")
            else:
                EX.append(Class.get('molecular_framework','NA'))

            # Alternative Parents
            AlternativeParentsList = Class.get('alternative_parents','NA')
            if AlternativeParentsList == 'NA':
                EX.append('NA')
            else:
                AlternativeParentsNames = []
                for item in AlternativeParentsList:
                    AlternativeParentsNames.append(item['name'])
                AlternativeParentsString = ", ".join(AlternativeParentsNames)
                EX.append(AlternativeParentsString)
            # Substituents
            SubstituentsList = Class.get('substituents','NA')
            if SubstituentsList == 'NA':
                EX.append("NA")
            else:
                SubstituentsString = ", ".join(SubstituentsList)
                EX.append(SubstituentsString)
            EX.append(Class.get('description','NA'))

            for item in EX:
                if item == None:
                    print(inchi_key)
                    print(EX)
                    print("NONE HERE")
            #Problematic apostrophes in the text need to be removed
            EX = ([s.replace('\'', '`') for s in EX if type(s) == str])
            EX = CopyDirectParent(EX)
        else:
            Print("UNKNOWN ERROR IN CODE, THIS SHOULDNT HAPPEN")
            FailedStructures.append("NA "+NP_ID[0])
            print(NP_ID[0])
            print(Class)

        sql = (f"UPDATE {table_name} SET {columns[0]}='{EX[0]}',"
               f"{columns[1]}='{EX[1]}', {columns[2]}='{EX[2]}',"
               f"{columns[3]}='{EX[3]}', {columns[4]}='{EX[4]}',"
               f"{columns[5]}='{EX[5]}', {columns[6]}='{EX[6]}',"
               f"{columns[7]}='{EX[7]}', {columns[8]}='{EX[8]}',"
               f"{columns[9]}='{EX[9]}', {columns[10]}='{EX[10]}',"
               f"{columns[11]}='{EX[11]}', {columns[12]}='{EX[12]}',"
               f"{columns[13]}='{EX[13]}', {columns[14]}='{EX[14]}'"
               f"WHERE {id_column} = '{NP_ID[0]}'")
        try:
            c.execute(sql)
        except sqlite3.OperationalError:
            print("Syntax Error occurred at: "+str(NP_ID))
            print(sql)
            FailedStructures.append(NP_ID[0])


    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

    OutputUnclassifiedStructures(ListUnclassified,ListEmpty,
                                 FailedStructures,TimeStamp)
    return None


def mainMIBIG(QueryIDDict, SqliteFile, TableName,
         Batched = False,
         TimeStamp = 000000):
    """Run Classyfire on all smiles of a column in a SQlite table

    Keyword Arguments:
        QueryIDDict -- Dictionary with 'compound_ID'_'compound_name' as key
        and a QueryID as value that can be used to retrieve ClassyFire
        classifications.
        SqliteFile -- Path to the SQlite database
        TableName -- Name of the table in the database to edit
        Batched -- Boolean, wheter to perform the classification in batches
        TimeStamp -- int/float, used to indicate when the output was created
    """
    sqlite_file = SqliteFile    # path of the sqlite database file
    table_name = TableName   # name of the table to be interacted with
    id_column = 'compound_id' # name of the PRIMARY KEY column
    compound_name_column = 'compound_name' # name of the compound name
    default_value = 'NA'
    # name of the new classification column
    columns = ['cf_kingdom','cf_superclass',\
    'cf_class','cf_subclass','cf_intermediate_0','cf_intermediate_1',\
    'cf_intermediate_2','cf_intermediate_3','cf_intermediate_4',\
    'cf_intermediate_5','cf_molecular_framework','cf_alternative_parents',\
    'cf_substituents', 'cf_description', 'cf_queryID']

    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file) # Connecting to the database
    c = conn.cursor() # Adding a cursor to interact with the database

    if Batched == False:
        column_type = 'TEXT'
        # Adding new column, if it does not exist yet, without a row value
        for new_column_name in columns:
            try:
                c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT {dv}"\
                    .format(tn=table_name, cn=new_column_name, ct=column_type, dv=default_value))
                print("Column created: {cn}".format(cn=new_column_name))
            except sqlite3.OperationalError:
                print("Column already exists: {cn}".format(cn=new_column_name))

    FailedStructures = []
    ListUnclassified = []
    ListEmpty = []
    for key, QueryID  in QueryIDDict.items():
        CompoundID, CompoundName = key.split('_')
        CompoundID = CompoundID.replace('\'', '`')
        CompoundName = CompoundName.replace('\'', '`')
        Class = GetSinglePyclassyfireResult(QueryID)
        if Class == False or Class == {}:
            WhereString = f"{id_column} LIKE '{CompoundID}%' AND {compound_name_column} == '{CompoundName}'"
            InteractWithSQL.UpdateTable(c,table_name,{'cf_queryID':QueryID},WhereString)
            InchiKeyWhereString = f"cf_queryID = '{QueryID}'"
            InchiKey = InteractWithSQL.GetFirstValue(c,table_name,InchiKeyWhereString,'rdkit_inchi_key')

            if InchiKey == False:
                print('No InchiKey')
                Class = False
            else:
                Class = PyClassify(InchiKey)

        if Class == False or Class == {}:
            print(key,"ClassyFire did not recoginize this structure")
            Class = {}
            ListUnclassified.append(key)
        else:
            EX = {}
            try:
                EX['cf_kingdom'] = Class.get('kingdom','NA').get('name','NA')
            except AttributeError:
                EX['cf_kingdom'] = 'NA'
            try:
                EX['cf_superclass'] = Class.get('superclass','NA').get('name','NA')
            except AttributeError:
                EX['cf_superclass'] = 'NA'
            try:
                EX['cf_class'] = Class.get('class','NA').get('name','NA')
            except AttributeError:
                EX['cf_class'] = 'NA'
            try:
                EX['cf_subclass'] = Class.get('subclass','NA').get('name','NA')
            except AttributeError:
                EX['cf_subclass'] = 'NA'
            try:
                for i in range(6):
                    Class['intermediate_nodes'].append({'name':'NA'})
                in0, in1, in2, in3, in4, in5 = Class['intermediate_nodes'][:6]
                EX['cf_intermediate_0'] = in0['name']
                EX['cf_intermediate_1'] = in1['name']
                EX['cf_intermediate_2'] = in2['name']
                EX['cf_intermediate_3'] = in3['name']
                EX['cf_intermediate_4'] = in4['name']
                EX['cf_intermediate_5'] = in5['name']
            except (KeyError, AttributeError)as e:
                EX['cf_intermediate_0'] = 'NA'
                EX['cf_intermediate_1'] = 'NA'
                EX['cf_intermediate_2'] = 'NA'
                EX['cf_intermediate_3'] = 'NA'
                EX['cf_intermediate_4'] = 'NA'
                EX['cf_intermediate_5'] = 'NA'

            try:
                EX['cf_molecular_framework'] = Class.get('molecular_framework','NA')
            except:
                EX['cf_molecular_framework'] = 'NA'


            # Alternative Parents
            AlternativeParentsList = Class.get('alternative_parents','NA')
            if AlternativeParentsList == 'NA':
                EX['cf_alternative_parents'] = 'NA'
            else:
                AlternativeParentsNames = []
                for item in AlternativeParentsList:
                    AlternativeParentsNames.append(item['name'])
                AlternativeParentsString = ", ".join(AlternativeParentsNames)
                EX['cf_alternative_parents'] = AlternativeParentsString

            # Substituents
            SubstituentsList = Class.get('substituents','NA')
            if SubstituentsList == 'NA':
                EX['cf_substituents'] = 'NA'
            else:
                EX['cf_substituents'] = ", ".join(SubstituentsList)

            # Description
            EX['cf_description'] = Class.get('description','NA')
            EX['cf_queryID'] = QueryID

            #Problematic apostrophes in the text need to be removed
            for key, value in EX.items():
                if type(value) == str:
                    EX[key] = value.replace('\'','`')
                elif type(value) == list:
                    NewList = []
                    for item in value:
                        if type(item) == str:
                            NewList.append(item.replace('\'', '`'))
                        else:
                            NewList.append(item)
                    EX[key] = NewList


            try:
                if not all(value == 'NA' for value in EX.values()):
                    WhereString = f"{id_column} LIKE '{CompoundID}%' AND {compound_name_column} == '{CompoundName}'"
                    InteractWithSQL.UpdateTable(c,table_name,EX,WhereString)
            except sqlite3.OperationalError:
                print("Syntax Error occurred at: "+str(key))
                print(sql)
                FailedStructures.append(key)


    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

    OutputUnclassifiedStructures(ListUnclassified,ListEmpty,
                                 FailedStructures,TimeStamp)
    return None


if __name__ == "__main__":
    start = time.time()
    #Input required: SqliteFile, TableName
    NPDB_IDs = SQL_IDS_to_List.main(
        sys.argv[1], sys.argv[2],IDcolumn = "compound_id")
    print("Nr of IDs: "+str(len(NPDB_IDs)))
    mainMIBIG(NPDB_IDs, sys.argv[1], sys.argv[2],
         Batched = False,
         TimeStamp = "MIBIG")

