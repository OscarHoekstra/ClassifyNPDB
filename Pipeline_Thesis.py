#!/usr/bin/env python3
"""
Author: Oscar Hoekstra
Student Number: 961007346130
Email: oscarhoekstra@wur.nl
Description: Runs the pipeline for linking the MIBiG and NPDB databases
"""
import time
import sys
import config
from Scripts import GetSqlIDs, InchiToSQL, ClassifyMibigCsv, MIBiGToSQL4
from Scripts import Run_pyclassyfire4
import pickle
#import SQL_IDS_to_List
#import Run_pyclassyfire4
#import os


def PrintTime():
	"""Print the current date and time on the screen."""
	CurTime = time.strftime("%d-%m-%Y %H:%M")
	print("It is currently: "+CurTime)


def interval(start,location = False, decimals = 2):
	Elapsed = time.time()-start
	if Elapsed < 600:
		IntervalTime = str(round(time.time()-start,decimals))+" Seconds"
	else:
		IntervalTime = str(round(time.time()-start)/60)+" Minutes"
	if location != False:
		print(IntervalTime+" at location "+str(number))
	newstart=time.time()
	return IntervalTime, newstart




if __name__ == "__main__":
    cfg = config.Settings()
    SkipSteps = cfg['SkipSteps']
    start = time.time()

    #InchiKeysFilePath = Args[1]
    #NPDBtableName = Args[3]
    #MIBiGtableName = Args[4]
    #MIBiGsmilesFile = Args[5]



    # Add all the arguments to a textfile that will later contain the
    # unclassified structures. This will make sure that I know which
    # datasets the file belong to.
    with open(cfg['UnclassifiedFile'], 'w') as w:
        w.write("Arguments: "+str(sys.argv)+"\n")


    # Can not skip step 1, NPDB_IDs is necessary for other steps
#1 Get a list with all IDs present in the NPDB
    print("__Starting Step 1__")
    PrintTime()
    NPDB_IDs = GetSqlIDs.main(cfg['SQLPath'],
                              cfg['NPDBtable'],
                              cfg['structure_id'])
    Interval,start = interval(start)
    print("Step 1 took "+Interval)

    if 2 not in SkipSteps:
#2 Get Inchi Keys from Sam/Rutger, Input into NPDB and combine 2
#seperate inchi_keys in NPDB into one.
        print("_____Starting Step 2")
        PrintTime()
        InchiToSQL.main(cfg['InchiKeyFile'],cfg['SQLPath'],
                        cfg['NPDBtable'],cfg['structure_id'])
        Interval,start = interval(start)
        print("_____Step 2 took "+Interval)


    if 3 not in SkipSteps:
#3 Put all of MIBiG into SQL Database and translate SMILES to Inchi_keys.
#  Then add smiles obtained from Michelle Schorn and get the classifications
#  with ClassyFire.
        print("_____Starting Step 3")
        PrintTime()
        #Adding Smiles from csv to mibig database

        #!!!
        MibigCompoundDict = ClassifyMibigCsv.LoadMibigCsv(cfg['MibigSmilesFile'])
        MIBiGToSQL4.main(cfg['SQLPath'],cfg['MibigTable'],MibigCompoundDict)
        with open(cfg['PQueryID'],"rb") as f:
            QueryIDDict = pickle.load(f)
        Run_pyclassyfire4.mainMIBIG(QueryIDDict,cfg['SQLPath'],cfg['MibigTable'],TimeStamp = cfg['StartTimestamp'])

        Interval,start = interval(start)
        print("_____Step 3 took "+Interval)

    if 4 not in SkipSteps:
#4 Run ClassyFire on NPDB and put results back into database
        print("_____Starting Step 4")
        PrintTime()
        ToClassify = Run_pyclassyfire4.GetToClassify(
            cfg['RedoClassify'],
            cfg['ToClassifyFile'],
            NPDB_IDs)

        BatchSize = cfg['BatchSize']
        if cfg['DoBatched'] == True:
            BatchedToClassify = [ToClassify[x:x+BatchSize] for x in range(0, len(ToClassify), BatchSize)]
        else:
            # Works the same as batched, just with a single batch.
            BatchedToClassify = [ToClassify]

        Progress = 0
        TotalNumber = len(ToClassify)
        try:
            Run_pyclassyfire4.AddColumns(cfg['SQLPath'],cfg['NPDBtable'])
            for Batch in BatchedToClassify:
                Run_pyclassyfire4.main(Batch, cfg['SQLPath'],
                    cfg['NPDBtable'],InchiColumn="inchi_key",
                    Batched = True, TimeStamp = cfg['StartTimestamp'])
                for item in Batch:
                    ToClassify.remove(item)
                with open(cfg['ToClassifyFile'], 'wb') as f:
                    pickle.dump(ToClassify, f) #basically removes the classified ids from the file
                Progress += BatchSize
                # Below writes and overwrites the progress, functioning
                # sort of like a progress bar.
                sys.stdout.write(str(Progress) +"/"+ str(TotalNumber) + " Structures Completed"+(" "*36))
                sys.stdout.flush()
                sys.stdout.write('\r')
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("You seem to have interupted the program while it was running PyClassyFire")
            print("All batches that have finished have been saved to the SQL database")
        print("_____Step 4 took "+Interval)


#5 Combine MIBiG and NPDB somehow

    ScriptEnd = time.time()
    print("Pipeline Finished!")
    print("The whole script took: "+str(round(ScriptEnd - cfg['ScriptStartingTime']))+ " Seconds")
