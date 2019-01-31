#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Adds different forms of the inchi-keys created by RDKit
to the NPDB table in the SQL file.
"""

import sqlite3
import time
import sys
from Scripts import InteractWithSQL as Sql


def InsertIntoSQL(cursor, file_path, table_name, id_column = 'structure_id'):
    """Parses a file with (space) seperated NP_ID strings, smiles and
    inchi-keys into a SQlite database.

    Keyword Arguments:
        cursor -- SQL cursor object to interact with the database
        file_path -- Path to the inchi-key file
        table_name -- Name of the table in the database to edit
        id_column -- Name of the column that contains the structure ids
    """
    # Adding molconvert inchi_keys to the database
    EX = {}
    with open(file_path) as f:
        for line in f:
            line = line.split()
            structure_id = line[0]
            # if there only is a neutral smile and inchi-key
            if len(line) == 3:
                inchi_key_molconvert =  line[-1]
                inchi_key_molconvert_neutral = inchi_key_molconvert
            # if there is a charged and a neutral smile and inchi-key
            elif len(line) == 5:
                inchi_key_molconvert = line[-1]
                inchi_key_molconvert_neutral = line[-2]
            else:
                print("Encoutered a problem with the inchikey file")
            EX['inchi_key_molconvert']= inchi_key_molconvert[9:]
            EX['inchi_key_molconvert_neutral']= inchi_key_molconvert_neutral[9:]

            # Adding the molconvert inchi-key to the database
            WhereString = f"{id_column} = '{structure_id}'"
            Sql.UpdateTable(cursor,table_name,EX,WhereString)
    return None


def CombineInchiKeys(cursor,table_name, id_column = 'structure_id'):
    """Combine the 2 seperate inchi-keys in the SQL database
    and add the charge similar to the molconvert charge to one copy
    and a neutral charge to the other.

    Keyword Arguments:
        cursor -- SQL cursor object to interact with the database
        table_name -- Name of the table in the database to edit
        id_column -- Name of the column that contains the structure ids
    """
    # Retrieving the structure_id, inchi-keys and the charges from the
    # molconvert inchi-keys.
    Structures = []
    EX = {}
    for Row in cursor.execute('SELECT structure_id, inchi_key1,'
            'inchi_key2, inchi_key_molconvert from '+table_name):
        Structures.append(Row[0])
        EX['inchi_key'] = Row[1]+'-'+Row[2][:8]+'SA-'+Row[3][-1]

    for item in Structures:
        # Adding the combined inchi-keys with the 'hopefully' correct charge
        WhereString = f"{id_column} = '{item}'"
        Sql.UpdateTable(cursor, table_name, EX, WhereString)
    return None


def main(FilePath,SqliteFile,TableName,IDcolumn = 'structure_id'):
    conn, c = Sql.Connect(SqliteFile)
    Sql.CreateNewTable(c,TableName,IDcolumn,
                       ColumnNames = ['inchi_key','inchi_key_molconvert',
                                      'inchi_key_molconvert_neutral'])
    InsertIntoSQL(c, FilePath, TableName, IDcolumn)
    Sql.Close(conn)
    return True


if __name__ == '__main__':
    StartTime = time.time()
    main(sys.argv[1],sys.argv[2],sys.argv[3])
    EndTime = time.time()
    if EndTime-StartTime < 300:
        print("Running InchiToSQL took "+\
         str(round(EndTime-StartTime))+" Seconds")
    else:
        print("Running InchiToSQL took "+\
         str(round(EndTime-StartTime)/60)+" Minutes")
