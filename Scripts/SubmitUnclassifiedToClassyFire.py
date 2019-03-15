#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Submit a list of smiles or inchis to ClassyFire and get
a dictionary with QueryIDs to retrieve results.
"""

import time
import sys
import sqlite3
import pyclassyfire.client
import pickle


def tsv_file_to_dict(input_file):
    """Parses the first two columns of a tsv file like they were a
    dictionary. The first column will be the key and the second a value"""
    out_dict = {}
    with open(input_file, "r") as f:
        data = f.readlines()
    for row in data:
        row = row.strip().split('\t')
        out_dict[row[0]] = row[1]
    return out_dict


def pyclassify_structure_list(compound_dict):
    """Submits a smile or inchi to the ClassyFire sevice and returns
    a query id which can be used to collect results

    Keyword Arguments:
        compound_dict -- dictionary with compound-id as key and smiles
                        or inchi as value.
    Returns:
        queryID_dict -- dicionary with compound-id as key and the query ID
                     that can be used to retrieve ClassyFire results
                     as the value.
    """
    queryID_dict = {}
    for key, compound in compound_dict.items():
        try:
            queryID_dict[key] = pyclassyfire.client.structure_query(compound)
        except Exception as e:
            print(e)
            print(key)
            print(compound)
    return queryID_dict




if __name__ == "__main__":
    print("SubmitUnclassifiedToClassyFire has started.")
    print("1st argument needs to structures tsv file, 2nd argument needs to be SQLite database file")
    script_start = time.time() # Time indicator for when the pipeline was started
    start_timestamp = time.strftime('%Y%m%d-%H%M%S')
    input_file = sys.argv[1]
    database = sys.argv[2]


    #Open file and load data into a dictionary
    structure_dict = tsv_file_to_dict(input_file)

    #Submit structures to ClassyFire and return a dictionary with QueryIDs
    query_dict = pyclassify_structure_list(structure_dict)

    #Saving a pickled version of the query_dict
    #Set skip_saving_output to True to not save the pickled query_dict
    skip_saving_output = False
    if skip_saving_output == False:
        out_file_name = "Output_SubmitUnclassifiedToClassyFire_"+start_timestamp+".txt"
        with open(out_file_name,'wb') as f:
            pickle.dump(query_dict, f)
            print("Saved",out_file_name)

    #Connecting the the SQLite database
    conn = sqlite3.connect(database) # Connecting to the database
    cursor = conn.cursor() # Adding a cursor to interact with the database

    #Add the cf_queryID column if it doesnt exist yet
    try:
        cursor.execute("ALTER TABLE structure ADD COLUMN 'cf_queryID' TEXT")
    except sqlite3.OperationalError:
        #Column already exists
        pass

    #Save the QueryIDs in the SQLite database
    for structureID, queryID in query_dict.items():
        cursor.execute(f"UPDATE structure SET cf_queryID = '{queryID}' WHERE structure_id = '{structureID}'")

    conn.commit()
    conn.close()


    script_end = time.time()
    print()
    print("SubmitUnclassifiedToClassyFire has finished!")
    print("The whole script took: "+str(script_end - script_start)+ " Seconds")
