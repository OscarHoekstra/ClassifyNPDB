#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Get the results of classification linking
"""

import time
import sys
import sqlite3
import pyclassyfire.client
import pickle


if __name__ == "__main__":
    print("CreateThesisResults has started.")
    print("1st argument needs to be the SQLite database, 2nd argument needs to be the tablename")
    # Initialization
    script_start = time.time()  # Time indicator for when the pipeline was started
    start_timestamp = time.strftime('%Y%m%d-%H%M%S')  # Timestamp for saving the output of this script
    database = sys.argv[1]
    tablename = sys.argv[2]
    
    # The name of the SQLite column with BGC class data and the available options.
    biosyn_class_column_name = "biosyn_class"
    biosyn_classes = ["RiPP","NRP","Polyketide","Other","Saccharide","Terpene","Alkaloid"]
    
    # The name of the ClassyFire column you want to use and the available options
    cf_column_name = "cf_superclass"
    cf_classes = ["NA","Lipids and lipid-like molecules","Organic acids and derivatives",
                  "Phenylpropanoids and polyketides","Organic oxygen compounds",
                  "Alkaloids and derivatives","Organoheterocyclic compounds","Benzenoids",
                  "Organosulfur compounds","Organic 1,3-dipolar compounds",
                  "Hydrocarbon derivatives","Organic Polymers","Organic nitrogen compounds",
                  "Nucleosides, nucleotides, and analogues","Hydrocarbons",]

    # Connecting the the SQLite database
    conn = sqlite3.connect(database)  # Connecting to the database
    c = conn.cursor()  # Adding a cursor to interact with the database

    # Getting all the linking data in a single array
    result_list = []
    for cf in cf_classes:
        for biosyn in biosyn_classes:
            c.execute(f"SELECT count(*) FROM {tablename} WHERE {cf_column_name} = '{cf}',
                      f"AND {biosyn_class_column_name} LIKE '%{biosyn}%'")
            result_list.append(c.fetchone())

    # Saving and closing the SQLite database
    conn.commit()
    conn.close()
    
    # Transforming the linking array into a TSV tablename
    result_table = []
    pref_i = 0
    for i in range(0,len(results),len(biosyn_classes)):
        i = i+len(biosyn_classes)
        result_table.append('\t'.join(result_list[pref_i:i]))
        pref_i = i
    
    # Output the table
    results = '\n'.join(result_table)
    print(results)

    # Ending of script
    script_end = time.time()
    print()
    print("SubmitUnclassifiedToClassyFire has finished!")
    print("The whole script took: "+str(script_end - script_start)+ " Seconds")
