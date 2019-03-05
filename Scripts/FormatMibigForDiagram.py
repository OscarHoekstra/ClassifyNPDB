#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Formats a Tsv copy of the MIBiG SQL table so it can be used
to create a rawgraphs.io alluvial diagram.
"""
import sys

if __name__ == "__main__":
    NewData = []
    FinalData = []
    with open(sys.argv[1], 'r') as f:
        Header = f.readline()
        Data = f.readlines()
    Data = [x.strip().split('\t') for x in Data]
    for line in Data:
        newline = line
        line[2] = line[2].split(', ')
        line[3] = line[3].split(', ')
        Length = len(list(zip(line[2], line[3])))
        line.append(str(1/Length))
        for item1, item2 in zip(line[2], line[3]):
            newline[2] = item1
            newline[3] = item2
            NewData.append('\t'.join(newline))
    # CountItems contains the column positions of which we want to know
    # the amount of values in that specific class
        # 2_biosyn_class, 3_biosyn_subclass, 23_kingdom, 24_superclass,
        # 25_class, 26_subclass
    CountItems = [23,24,25,26,27,28,29,30]
    DictList = []
    for k in range(len(line)):
        DictList.append({})
    Data = [x.strip().split('\t') for x in NewData]
    for line in Data:
        print(DictList)
        print(line[-1])
        try:
            DictList[2][line[2]] += 1
            DictList[3][line[3]] += 1
        except:
            DictList[2][line[2]] = 1
            DictList[3][line[3]] = 1
        for i in CountItems:
            try:
                DictList[i][line[i]] += float(line[-1])
            except:
                DictList[i][line[i]] = float(line[-1])
    for line in Data:
        line[2] = str(round(DictList[2][line[2]])) + ': ' + line[2]
        line[3] = str(round(DictList[3][line[3]])) + ': ' + line[3]
        for i in CountItems:
            line[i] = str(round(DictList[i][line[i]])) + ': ' + line[i]
        FinalData.append('\t'.join(line))

    FinalData = [Header.strip()+'\tSize'] + FinalData
    FinalData = '\n'.join(FinalData)
    with open('Formated'+sys.argv[1], 'w') as f:
        f.write(FinalData)
    print('FormatMibigForDiagram.py has finished!')
