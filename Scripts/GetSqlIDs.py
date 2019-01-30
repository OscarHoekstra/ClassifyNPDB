#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Get all the NP_IDs from the NPDB and puts them in a list.
"""
import sqlite3
import sys
from Scripts import InteractWithSQL as Sql

def Retrieve_NP_IDs(sqlite_file,table_name,id_column = "structure_id"):
    """Retrieves all NP_IDs from the SQlite database and adds them to a list

    Keyword Arguments:
        sqlite_file -- Path to the SQlite database
        table_name -- Name of the table in the database to edit
        id_column -- Name of the column that contains the IDs we want
    Returns:
        NPDB_ID_List -- List with NP_IDs
    """
    # Connecting to the database file
    conn, c = Sql.Connect(sqlite_file)

    # Adding the NP_IDs to a list
    NPDB_ID_List = []
    for ID in c.execute(f'SELECT {id_column} from {table_name}'):
        NPDB_ID_List.append(ID)

    # Committing changes and closing the connection to the database file
    Sql.Close(conn)
    return NPDB_ID_List

def main(SqliteFile,TableName,IDcolumn):
    NPDB_IDs = Retrieve_NP_IDs(SqliteFile,TableName,IDcolumn)
    print("Retrieved NP_IDs and added them to a List")
    return NPDB_IDs


if __name__ == '__main__':
    NPDB_IDs = main(sys.argv[1],sys.argv[2],sys.argv[3])
    print(len(NPDB_IDs))
    print(sys.getsizeof(NPDB_IDs))
    #print(NPDB_IDs)
