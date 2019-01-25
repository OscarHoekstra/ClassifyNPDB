#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Configuration file for my pipeline.
    Edit anything after the colon or between the single quotes to
    run the pipeline with your own settings and files.
"""
import time


def Settings():
    Workbase = '/mnt/scratch/hoeks102/Thesis_Bsc/Workbase/'
    ScriptFolder = Workbase+'Scripts/'
    InFilesFolder = Workbase+'InFiles/'
    OutFilesFolder = Workbase+'OutFiles/'
    Start = time.time()
    StartTimestamp = time.strftime('%Y%m%d-%H%M')

    cfg = {
# General Settings
        # Starting time of the script is set automatically and used to
        #save certain output with a timestamp.
        "ScriptStartingTime": Start,
        "StartTimestamp": StartTimestamp,

        # Add a number to this set to skip that step of the pipeline.
        "SkipSteps": (0,3),

# File Paths
        # Path to the SQL database that the script works with:
        "SQLPath": Workbase+'Natural_Product_Structure.sqlite',
        # Path to the file with the inchi-keys for the NPDB create
        # by molconvert, with credits to Rutger Ozinga
        "InchiKeyFile": InFilesFolder+'all_input_structures_neutralized_full_dataFile.txt',

# Settings about NPDB table in the SQL database.
        # Name of the table in the database that contains the NPDB
        #structure data:
        "NPDBtable": 'structure',
        # Name of the column with the structure IDs:
        "structure_id": 'structure_id',


# Settings about the (to be created) MIBiG table in the SQL database.
            # Name of the table in the database that contains the
            #MIBiG data:
            "MibigTable": 'mibig',
            # Name of the column with the compound IDs:
            "compound_id": 'compound_id',


# Settings about files that will be outputted
        # Name of the file that will contain unclassified structures:
        "UnclassifiedFile": 'UnclassifiedStructures-'+StartTimestamp+".txt"

    }
    return cfg
