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
        result_list.append(cf) # Makes sure every row starts with the CF name
        for biosyn in biosyn_classes:
            # This gets the actual number and adds it to the result
            #print(f"SELECT count(*) FROM {tablename} WHERE {cf_column_name} = '{cf}' AND {biosyn_class_column_name} LIKE '%{biosyn}%'")
            c.execute(f"SELECT count(*) FROM {tablename} WHERE chem_struct != 'NA' AND {cf_column_name} = '{cf}' AND {biosyn_class_column_name} LIKE '%{biosyn}%'")
            result_list.append(str(c.fetchone()[0]))

    # Get the total structures in each BGC class and each CF class
    cf_list = []
    biosyn_list = []
    for cf in cf_classes:
        c.execute(f"SELECT count(*) FROM {tablename} WHERE chem_struct != 'NA' AND {cf_column_name} = '{cf}'")
        cf_list.append(str(c.fetchone()[0]))
    for biosyn in biosyn_classes:
        c.execute(f"SELECT count(*) FROM {tablename} WHERE chem_struct != 'NA' AND {biosyn_class_column_name} LIKE '%{biosyn}%'")
        biosyn_list.append(str(c.fetchone()[0]))

    # Saving and closing the SQLite database
    conn.commit()
    conn.close()


    # Transforming the linking array into a TSV tablename
    biosyn_classes = ["x"] + biosyn_classes  # "x" is the very first cell
    result_table = ['\t'.join(biosyn_classes)]
    pref_i = 0
    for i in range(0,len(result_list),len(biosyn_classes)):
        i = i+len(biosyn_classes)
        result_table.append('\t'.join(result_list[pref_i:i]))
        pref_i = i

    # Output the table and other data
    results = '\n'.join(result_table)
    output_text = "Total structures in each CF class\r\n"
    output_text += '\t'.join(cf_list) + "\r\n"
    output_text += "\r\nTotal structures in each BGC class\r\n"
    output_text += '\t'.join(biosyn_list) + "\r\n"

    print(results)
    print()
    print(output_text)
    print("Output also available as file: ThesisResultOutput.txt")
    with open("ThesisResultOutput.txt","w") as f:
        f.write(results)
        f.write('\r\n\r\n\r\n')
        f.write(output_text)


    # Ending of script
    script_end = time.time()
    print()
    print("SubmitUnclassifiedToClassyFire has finished!")
    print("The whole script took: "+str(script_end - script_start)+ " Seconds")
