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
    Start = time.time()
    StartTimestamp = time.strftime('%Y%m%d-%H%M')

    cfg = {
# General Settings
        # Add a number to this set to skip that step of the pipeline.
        # Step 1 can not be skipped as its necessary for further steps
        # and it is also really short.
        "SkipSteps": (0,),

        # The amount of BGCs that should be missing before the script will
        # assume it is at the end and stop:
        "MaxMibigFails": 10,

        # Do the classification of the NPDB in batches? (Classifications are
        # saved in between, crashes are less severe but more batches take
        # longer)
        "DoBatched": True,

        # Batch size (standard 10-100)?
        "BatchSize": 50,
        # Re-do all the NPDB classifications, usefull for if something
        # might have updated
        # Set this to true to always re-do the classification.
        "RedoClassify": True,


# General Constants
        # Starting time of the script is set automatically and used to
        #save certain output with a timestamp.
        "ScriptStartingTime": Start,
        "StartTimestamp": StartTimestamp,

# File Paths
        # Path to the SQL database that the script works with:
        "SQLPath": Workbase+'Natural_Product_Structure.sqlite',

        # Path to the file with the inchi-keys for the NPDB create
        # by molconvert, with credits to Rutger Ozinga
        "InchiKeyFile": InFilesFolder+'all_input_structures_neutralized_full_dataFile.txt',

        # Path to the TSV file with Mibig compound_id and (new) smile,
        # with credits to Michelle Schorn.
        "MibigSmilesFile": InFilesFolder+'All_MIBiG_compounds_with_SMILES_and_PMID_MAS.txt',

        # Path to the file that countains a pickled (saved in bytes)
        # copy of the QueryIDDict, which contains the IDs that still
        # need to be classified by ClassyFire.
        "PQueryID": Workbase+'PickledQueryIDDict.txt',

        # Path to file with the still to be classified NPDB IDs:
        "ToClassifyFile": Workbase+'ToClassify.txt',

# Settings about NPDB table in the SQL database.
        # Name of the table in the database that contains the NPDB
        #structure data:
        "NPDBtable": 'structure', #standard:'structure'

        # Name of the column with the structure IDs:
        "structure_id": 'structure_id', #standard:'structure_id'

        # Name of the column with inchi-keys to get classifications for:
        "InchiKeyToClassify": 'inchi_key' #standard:'inchi_key'


# Settings about the (to be created) MIBiG table in the SQL database.
        # Name of the table in the database that contains the
        #MIBiG data:
        "MibigTable": 'mibig',#standard:'mibig'

        # Name of the column with the compound IDs:
        "MibigCompoundID": 'compound_id', #standard:'compound_id'


# Settings about files that will be outputted
        # Name of the file that will contain unclassified structures:
        "UnclassifiedFile": 'UnclassifiedStructures-'+StartTimestamp+".txt"

    }
    return cfg
