# Classify Natural Product Database (ClassifyNPDB)

I created this project during my Bachelor Thesis at the Bioinformatics group at the WUR. 
My main research goal was to try to improve the linking of NPS (Natural Product Structures) to BGCs (Biosynthetic Gene Clusters) through classification. To do this I created a pipeline that i called classifyNPDB (Classify Natural Product Database) that is mostly split up into two parts, NPS and MIBiG. The goal was to collect the necessary data and obtain classification of the MIBiG structures to compare them to the BGC classification. Furthermore, it needed to be able to add classifications to the in-house NPDB (explained below). The pipeline was specifically created for my use case and the data I had access to, but I made it modular so you can enable or disable parts to make it run with your dataset and produce and output of your desire.

The pipeline will automatically retrieve the BGC data from the [MIBiG](https://mibig.secondarymetabolites.org/repository.html) database. This database contains both information about biosynthetic gene clusters and the chemical compounds produced from these clusters. This is crucial because it allows us to link the classification of the clusters to the classification of the structures. ClassifyNPDB adds each structure with information about the BGC it belongs to, including class data, and the necessary information about the structure itself to a SQL database.

For the NPS part the pipeline can start from any list or database of InChIKeys or SMILES strings. I will however start with an in-house SQL database with information about a lot of structures (currently ~300.000). This includes things like an identifier, mass, inchi, inchi-key, smile, mol-formula and class data. It is however only necessary to have identifiers and an InChIKey, or a seperate file with InChIKeys for each identifier to run the pipeline.                                   

ClassyFire is then used to automatically produce classifications of structures of both databases. The MIBiG data will then have BGC class data and structure class data. These classifications can be compared and hopefully be used to improve the linking between BGCs and Natural Products.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To run this pipeline or to make use of the scripts, you will need Python3 and Sqlite3.
Since many of the scripts use f-Strings it is recommended that you use Python 3.6 or higher. Otherwise all these f-Strings will not work and need to be edited to an older way to format strings.
The version of SQlite3 should not matter, but I used the latest (SQLite version 3.26.0 (2018-12-01))

There are also three python packages required: requests , rdkit and pyclassyfire.
I recommend setting up a conda enviroment with the packages.
```
#linux:
#NOTE: replace 'myenv' with your environment name of choice 
conda create -n myenv python=3.7.2 requests rdkit
conda activate myenv
```

Then go into your working directory and use the following commands to download and install pyclassyfire.
Since requests is a dependency of pyclassyfire, you could have left it out in the conda create command and it would still install it here.
```
#linux:
git clone https://github.com/JamesJeffryes/pyclassyfire.git
cd pyclassyfire
python setup.py install
```

### Installing

To download and install the actual scripts and necessary files of my pipeline you could either go to the following github link and download the zip or use the following git commands to automatically do it.

```
#git
git clone https://github.com/OscarHoekstra/ClassifyNPDB.git
```

## Running the pipeline

### Testing dependencies

To test if all dependencies were set-up correctly and if the pipeline will run on your system you could disable the running of all steps in the config.py (how will be explained below). If no Errors occur, than everything should be setup correctly to run the pipeline.

### Setting up the config

The settings of the pipeline are defined in a file called config.py. This is a python script with a single function that returns a dictionary with the settings. 
Edit anything after the colon or between the single quotes in the config.py file to run the pipeline with your own settings and files.
To skips certain steps of the pipeline, you can add numbers to the SkipSteps set.
```
#Example:

def Settings():
  Workbase = '/mnt/scratch/hoeks102/Thesis_Bsc/Workbase/'
  cfg = {
  # General Settings
          # Add a number to this set to skip that step of the pipeline.
           "SkipSteps": (0,3),
  
  # File Paths
          # Path to the SQL database that the script works with:
          "SQLPath": Workbase+'Natural_Product_Structure.sqlite'
         }
  return cfg
```
These settings are then retrieved in the pipeline with the following code:
```
import config
cfg = config.Settings() # Load the settings with which to run the pipeline.
SkipSteps = cfg['SkipSteps'] # Which steps of the pipeline to skip
NPDB_IDs = GetSqlIDs.main(cfg['SQLPath'], cfg['NPDBtable'], cfg['structure_id'])
```

### Running of the pipeline

After entering the correct settings in config.py the the actual execution of the pipeline is really simple.
Just execute Pipeline_Thesis.py with python3. Any other arguments will be saved and used in the creation of the UnclassifiedStructures file. This way you could add notes to remember when looking at the results of the pipeline. 

```
#Example:
python3 Pipeline_Thesis.py "Running pipeline with a new version of the MIBiG database" "all Structure database steps skipped".

#Will result in a file 'UnclassifiedStructures-DATE-TIME.txt' that will start with the line:
Arguments: ['Pipeline_Thesis.py', 'Running pipeline with a new version of the MIBiG database', 'all Structure database steps skipped']
```

## Built With

* [Python3](https://www.python.org/) - All Scripts
* [Sqlite3](https://www.sqlite.org/index.html) - Database Management
* [RDKit](https://www.rdkit.org/docs/api-docs.html) - Python API to generate SMILES and InChIKeys
* [ClassyFire](http://classyfire.wishartlab.com/) - Automated structural classification of chemical entities
* [pyclassyfire](https://github.com/JamesJeffryes/pyclassyfire) - Python API with helper functions for using ClassyFire
* [MIBiG](https://mibig.secondarymetabolites.org/repository.html) - Biosynthetic Gene Cluster Data

## Versioning

No versioning was used for this project. It was only near the end of my thesis that I got a fully working version on which only minor changes were made. That is why I just released the full version at the end. This does not mean however that I managed to implement all the features I wanted and there is still a lot to be added.

## Authors

* **Oscar Hoekstra** - *Construction of pipeline* - (https://github.com/OscarHoekstra)

See also the list of [contributors](https://github.com/OscarHoekstra/Thesis_Bsc_Oscar/contributors) who participated in this project.

## Acknowledgments

All the code in this project was written by me (Oscar), but I had a lot of help from people with my code and the data I used. That is why I want to thank the following people:
* Justin van der Hooft: Thesis Supervisor
* Marnix Medema: Thesis Supervisor and Lead author MIBiG
* Sam Stokman: For the NPDB database and support with my thesis
* Rutger Ozinga: For the NPDB InChIKeys and support with my thesis
* Michelle Schorn: For the extended MIBiG SMILES file.

----------------------------------------------------------------------------------------------------------------------------------------
## Explanation of Scripts

### ClassifyNPDB.py
This is the main script that runs the pipeline and in which the other scripts are used.
It is seperated into 7 steps:
1. Retrieving a list of the present structure identifiers from the SQL database. This list is used by the other scripts.
2. Load a file with (molconvert) InChIKeys for each identifier and add them to the SQL database.
3. Combine a split InChIKeys back into a single one. (see explanation of Natural_Product_Structure.sqlite)
4. Create a dictionary with structures present in the MIBiG SMILES TSV file
5. Load the important data from the MIBiG database into a new table of the SQL.
6. Get Classifications for the MIBiG data.
7. Get Classification for the NPDB data

The scripts below are executed with the pipeline. You can however also the seperate scripts if you only want to perform a specific funtion. Do not you will likely need to edit the "if __name__ == '__main__':" part of the scripts to make them function in the way you intend.

### InteractWithSQL.py
This script contains a bunch of functions that simplify and streamline the interaction with a sqlite database through python.
The functions are self explanatory or explained in the docstring.

### GetSqlIDs.py
This script has a single purpose and could also theoretically have been a single function of the pipeline. It gathers all the structure IDs from the NPDB table and adds them to a list. This list can be used by other functions to loop over all structures.

### InchiToSQL.py
This scripts has 2 functions, one for step 2 and one for 3.
InsertIntoSQL is meant to take the InChIKeys from a file (all_input_structures_neutralized_full_dataFile.txt) and add them to the sqlite database.
CombineInchiKeys is used to merge two parts of a split InChIKey (see explanation of NPDB).

### ClassifyMibigTsv.py
The original goal of this script was to classify all of the SMILES present in the MIBiG database. For the final pipeline this script is only used because it contains a function that I could use to create a dictionary of the file All_MIBiG_compounds_with_SMILES_and_PMID_MAS.txt. The dictionary has compoundID_compoundName as key and the SMILES as value.

### MIBiGToSQL4.py
The main function of the MIBiGToSQL4 script is to add a table to the sqlite database with all the important data out of the MIBiG database. It does this by interating through all possible BGC codes (BGC#######) and trying to download the json file from https://mibig.secondarymetabolites.org/repository/BGC#######/BGC#######.json. 

Since each BGC might contain multiple structures, a new identifier is created from BGCaccession_CompoundName. The script then filters data out of the json and adds them to appropriate columns in the sqlite database.

### Run_pyclassyfire4.py
Run_pyclassyfire4 is split into 2 main funtions, one for the MIBiG data and one for the NPS data. Altough both of these parts have the same goal of retrieving classifications for the structures, they function quiet differently and I will thus explain them seperately below.
Both parts contain an option to perform the classification in batches of a user defined size. This is done because if a crash occurs during the classification for any reason it is possible that previous classifications are not saved. It is therefore highly recommended to activate this option since the classification takes a decently large amount of time and batching only increases this time by a negligible amount.
The batching works by creating a file (ToClassify.txt) with the structures that need to be classified (done automatically). Once the classification of a batch has been finished and saved, the structures are removed from the file. If an error occurs and you try to run the script again it will try to load the file and see which structures still need to be classified. The problem with this is that if you change the data without deleting ToClassify.txt or changing the RedoClassify to true, it will not recognise that there are new structures to classify. I recommend setting RedoClassify to True unless you have crashes.

This script also contains some old functions that aren't used any longer. They may however still be usefull for, as an example, testing the speed of ClassyFire with your setup (TestClassyfireSpeed()) or getting quick classifications for a list of InChIKeys (PyClassifyList()).

* MIBIG
For the MIBiG data the classifications are retrieved with the SMILES string. This usually takes longer because while with inchi-keys you can retrieve existing classifications, with SMILES ClassyFire first translates them to an InChIKey tries to find an existing classification and if that doesn't exist it tries to create a classification.
I created a way to prepare this classification beforehand to decrease running time of the pipeline. PyClassifyStructureList() is used to submit a list of SMILES or InChIs to ClassyFire and for each structure a query_id is created and saved. Once the classification has finished this query_id can then be used to retrieve the results of the classification. If the SMILES string did not give a classification it will try to use the rdkit_inchi_key. This is because I found that sometimes the SMILES did not work but the InChIKey created from that SMILES would give a ClassyFire result. This helps get a bit better performance in retrieving classification for the MIBiG classifications.

* NPS
NPS classifications are retrieved only through InChIKeys.
The InChIKey is retrieved from the database and the classification is retrieved with the PyClassify function. This uses pyclassyfire to basically search for the json file available for the InChIKey. It tries to create 4 different versions of the starting InChIKey to create the most highest possibility of classification.
The classification results are added to the SQLite database and also saved as a seperate file with the InChIKey used as name.

###FormatMibigForDiagram2.py
This script is not part of the main pipeline, and is used to format an output of the mibig table so it can be used in RAWGraphs.io.
To get an appropiate file to use as input use the following settings in SQLite: 
```
#SQLite
.headers on
.mode tabs
.once outputfile.txt --prints the result of the following command to outputfile.txt
SELECT * FROM mibig WHERE 1 --replace "1" with a search query to narrow results
```

###SubmitUnclassifiedToClassyFire.py
With this script, that is not implemented into the main pipeline, you can send SMILES from the NPDB to ClassyFire and save the QueryID that is generated with the correct structure_id in the database. It requires a TSV input file with structure_id as first column and SMILES or InChI as second column.

###CreateThesisResults.py
This script creates a table that contains the amount of linking between BGC classes and ClassyFire SuperClasses (or others).
You can divide a row by the total structures in that Superclass to get the percentage chance of finding a BGC class for each CF class, or a column by the total structures in that BGC class ot get the percentage chance of finding a Superclass in each BGC class.
See Thesis Result Excel for example.

## Explanation of Files

### Natural_Product_Structure.sqlite
This is the sqlite database that I started with and appended to. It was created by Sam Stokman and at the time of writing she is working on a new version. My pipeline will still work with the new pipeline, but a lot of the steps will become unnecessary and some settings will need to be changed. This database contained 3 tables: data_source, structure and structure_has_data_source.

1. data_source
This table has 2 column: source_name and nr_of_structures.
This table tells the reader how many structures come from each data source and thus the columns are self-explanatory
I don't use this table in my project.

2. structure
Columns: structure_id, monoisotopic_mass, inchi, smile, inchi_key2, inchi_key1, molecular_formula, kingdom, superclass, class, subclass.
   - structure_id is an unique identifier formatted as: NP_ID_# with # being any number counting up from 1.
   - [inchi](https://en.wikipedia.org/wiki/International_Chemical_Identifier) is a textual identifier for a structure and formated as: InChI=......
   - smile contains SMILES strings which are another way to write down structures.
   - inchi_key2 and inchi_key1 contain a split up version of an [InChIKey](https://en.wikipedia.org/wiki/International_Chemical_Identifier#InChIKey) which is a hashed version of the InChI.
   - inchi_key1 contains the first 14 characters of the key containing the connectivity information.
   - inchi_key2 contain the following 8 containing the stereochemistry information. Because of this weird split up version the charge information is lost and in a future version of the database a full InChIKey will be given, but I had to adapt my script around this.
   - kingdom -> subclass are classification imported from the sources that the rest of the data originates from. We didn't know the quality of this classification and we also wanted to other data that ClassyFire gives us, so that is why we add classification data to this. When we have the new classifications data we can also compare it to the old class data.

3. structure_has_data_source
This table contains 4 columns: structure_source_id, structure_id, source_id and source name.
This links all structures to where they originate from. I didn't use this table in my project.

### all_input_structures_neutralized_full_dataFile.txt
This is a space-seperated file with 5 columns. It contains the the InChIKeys created with rdkit by Rutger Ozinga.
The first column always contains a NP_ID. This is proceeded by the SMILES of this structure and if this structure is charged another neutral version of this SMILES.
Then follows 1 or 2 InChIKeys translated from the SMILES with RDKit.

### All_MIBiG_compounds_with_SMILES_and_PMID_MAS.txt
This is a tab-seperated with 4 columns that I create from an excel file. It contains the new and updates smiles of the MIBiG database created by Michelle Schorn.
The first column contains the MIBiG accession, the second the compound name, the third the SMILES and the last PMID/DOI.

### ToClassify.txt
This file is a pickled/byte-data version of the ToClassify list which contains the structure_ids which haven't been classified yet. The file can be read by  using pickle.load().

### PickledQueryIDDict.txt
This file a pickled/byte-data version of the dictionary that has structure_id as key and ClassyFire queryid as value. It can be used to retrieve the classifications of the structures which you submitted earlier.You can load it with pickle.load().

### FailedStructures
This contains the structures_ids which for one reason or another caused an error while trying to get classifications.
