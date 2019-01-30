#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Set of functions to generalise and simplify the interacting
with SQL databases in python.
"""
import sqlite3
import sys

def Connect(SqliteFile):
    """Make a connection with the sqlite database and add a cursor"""
    conn = sqlite3.connect(SqliteFile) # Connecting to the database
    cursor = conn.cursor() # Adding a cursor to interact with the database
    return conn, cursor

def Close(conn):
    """Close the connection to a sql database"""
    conn.commit()
    conn.close()
    return True

def DictToSQLQuery(QueryDict):
    """Translates a dictionary into 2 lists that can be used in SQL queries.
    The key is the column-name and the value the value that the column
    should become.
    """
    Columns = []
    Values = []
    for key, item in QueryDict.items():
        Columns.append(key)
        Values.append(item)
    return tuple(Columns), tuple(Values)

def CreateNewTable(cursor,TableName,PrimaryKeyColumnName,ColumnNames = [],ColumnType = "TEXT"):
    """Creates a new SQL table if it does not exists and all missing
       columns if it does.
    """
    cursor.execute("CREATE TABLE IF NOT EXISTS {tn} ('{pkcn}' {ct} PRIMARY KEY)"
    .format(tn=TableName, pkcn=PrimaryKeyColumnName, ct=ColumnType))
    for column_name in ColumnNames:
        try:
            cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn=TableName, cn=column_name, ct=ColumnType))
        except sqlite3.OperationalError:
            #print('sqlite3.OperationalError at InteractWithSQL.py when adding column')
            pass
    return True

def InsertOrUpdate(cursor, TableName, QueryDict):
    """Insert a new row into table, or if the primary key already exists
    update the row with the values supplied.
    """
    Columns, Values = DictToSQLQuery(QueryDict)
    try:
        cursor.execute(f"REPLACE INTO {TableName} {Columns} VALUES {Values}")
    except sqlite3.OperationalError:
        print(f'InsertOrUpdate: sqlite3.OperationalError at {Values}')
        return False
    return True

def UpdateTable(cursor, TableName, QueryDict, WhereString):
    """Update the table where the WhereString is true with the supplied
    values."""
    try:
        Query = ""
        for key, item in QueryDict.items():
            Query += f"{key} = '{item}', "
        Query = Query[:-2]
        cursor.execute(f"UPDATE {TableName} SET {Query} WHERE {WhereString}")
    except sqlite3.OperationalError:
        print(f'UpdateTable: sqlite3.OperationalError at {WhereString}')
        print(f"UPDATE {TableName} SET {Query} WHERE {WhereString}")
        return False
    return True

def GetFirstValue(cursor, TableName, WhereString, ReturnColumn):
    """Return the first result produced by the WhereString"""
    try:
        cursor.execute(f"SELECT {ReturnColumn} FROM {TableName} WHERE {WhereString}")
        Result = cursor.fetchone()
        if Result == None:
            return False
    except sqlite3.OperationalError:
        print(f'GetFirstValue: sqlite3.OperationalError at {WhereString}')
        print(f"SELECT {ReturnColumn} FROM {TableName} WHERE {WhereString}")
        return False
    return Result[0]

if __name__ == "__main__":
    print("Nothing Here")
