#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Formats a Tsv copy of the MIBiG SQL table so it can be used
to create a rawgraphs.io alluvial diagram.
"""
import sys

def removeUnnecessaryColumns(Header, Dataset, ColumnsToKeep = None):
    if ColumnsToKeep == None:
        Output = Dataset
    else:
        Output = []
        Header = Header.strip().split('\t')
        NewHeader = []
        for col in ColumnsToKeep:
            NewHeader.append(Header[col])
        Header = '\t'.join(NewHeader)
        for line in Dataset:
            newline = []
            for col in ColumnsToKeep:
                newline.append(line[col])
            Output.append(newline)
    return Header, Output





if __name__ == "__main__":
    NewData = []
    FinalData = []
    with open(sys.argv[1], 'r') as f:
        Header = f.readline()
        Data = f.readlines()
    Data = [x.strip().split('\t') for x in Data]
    # 2_biosyn_class, 3_biosyn_subclass, 23_kingdom, 24_superclass,
    # 25_class, 26_subclass
    ColumnsToKeep = [2,3,23,24,25,26,27,28,29,30,31,32]
    Header, Data = removeUnnecessaryColumns(Header, Data, ColumnsToKeep)
    for sublist in Data:
        sublist.append(str(1/(1+sublist[0].count(', '))))
    DictList = []
    for n in range(len(Data[0])):
        DictList.append({})
    for i in range(len(Data)):
        if ',' in Data[i][0]:
            Data[i][0] = Data[i][0].split(', ')
            Data[i][1] = Data[i][1].split(', ')
        for k in range(len(Data[i])):
            if type(Data[i][k]) == list:
                for item in Data[i][k]:
                    try:
                        DictList[k][item] += 1
                    except KeyError:
                        DictList[k][item] = 1
            else:
                try:
                    DictList[k][Data[i][k]] += 1
                except KeyError:
                    DictList[k][Data[i][k]] = 1
    for Compound in Data:
        if type(Compound[0]) != list:
            NewData.append(Compound)
        else:
            NewCompound = Compound[:]
            for m in range(len(Compound[0])):
                NewCompound[0] = Compound[0][m]
                NewCompound[1] = Compound[1][m]
                NewData.append(NewCompound)

    for x in range(len(NewData)):
        NewList = []
        for y in range(len(NewData[x])-1):
            NewList.append(str(DictList[y][NewData[x][y]]) + ': ' + str(NewData[x][y]))
        NewList.append(str(NewData[x][-1]))
        FinalData.append('\t'.join(NewList))


    FinalData = [Header.strip()+'\tSize'] + FinalData
    FinalData = '\n'.join(FinalData)
    with open('FixedFormated'+sys.argv[1], 'w') as f:
        f.write(FinalData)
    print('FormatMibigForDiagram2.py has finished!')
