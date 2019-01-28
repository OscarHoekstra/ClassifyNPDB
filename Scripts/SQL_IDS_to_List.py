#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Description: Get all the NP_IDs from the NPDB and puts them in a list
for easier looping.
"""
import sqlite3
import sys

def Retrieve_NP_IDs(SqliteFile,TableName,IDcolumn = "structure_id"):
    """Retrieves all NP_IDs from the SQlite database and adds them to a list

    Keyword Arguments:
        SqliteFile -- Path to the SQlite database
        TableName -- Name of the table in the database to edit
    Returns:
        NPDB_ID_List -- List with NP_IDs
    """
    sqlite_file = SqliteFile    # path of the sqlite database file
    table_name = TableName   # name of the table to be edited
    id_column = IDcolumn # name of the PRIMARY KEY column

    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file) # Connecting to the database
    c = conn.cursor() # Adding a cursor to interact with the database

    # Adding the NP_IDs to a list
    NPDB_ID_List = []
    for ID in c.execute('SELECT {idc} from {tn}'.format(
                        idc=IDcolumn, tn=table_name)):
        NPDB_ID_List.append(ID)

    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()
    return NPDB_ID_List

def main(SqliteFile,TableName,IDcolumn):
    NPDB_IDs = Retrieve_NP_IDs(SqliteFile,TableName,IDcolumn)
    print("Retrieved NP_IDs and added them to a List")
    return NPDB_IDs


if __name__ == '__main__':
    NPDB_IDs = main(sys.argv[1],sys.argv[2])
    print(NPDB_IDs)
