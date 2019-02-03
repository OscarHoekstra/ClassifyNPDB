# Extended Natural Product Database Pipeline (eNPDB)

I created this project during my Bachelor Thesis at the Bioinformatics group at the WUR. 
My main research goal was to try to improve the linking of NPS (Natural Product Structures) to BGCs (Biosynthetic Gene Clusters) through classification. 

I will start with an in-house SQL database with information about a lot of structures (currently ~300.000). This includes things like an identifier, mass, inchi, inchi-key, smile, mol-formula and class data. It is however only necessary to have identifiers and a inchi-key, or a seperate file with inchi-keys for each identifier to run the pipeline.

For the BGC data i'm going to use the [MIBiG](https://mibig.secondarymetabolites.org/repository.html) database. This database contains both information on the chemical compounds produced from the pathway as well as class data about the BGC.

ClassyFire is then used to automatically produce classifications of structures of both databases. The MIBiG data will then have BGC class data and structure class data. These classifications can be compared hopefully be used to improve the linking between BGCs and Natural Products.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To run this pipeline or to make use of the scripts, you will need Python3 and Sqlite3.
Since many of the scripts use f-Strings it is recommended that you use Python 3.6 or higher. Otherwise all these f-Strings will not work and need to be eddited to an older way to format strings.
The version of SQlite3 should not matter, but I used the latest (SQLite version 3.26.0 (2018-12-01))

There are also two python packages required: requests and rdkit.
I recommend setting up a conda enviroment with the packages.
```
#linux:
#NOTE: replace 'myenv' with your environment name of choice 
conda create -n myenv python=3.7.2 requests rdkit
conda activate myenv
```

### Installing

To download and install the actual scripts and necessary files of my pipeline you could either go to the following github link and download the zip or use the following git commands to automatically do it.

```
#git
git clone git://github.com/OscarHoekstra/Thesis_Bsc_Oscar.git
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
* [RDKit](https://www.rdkit.org/docs/api-docs.html) - Python API to generate SMILES and Inchi-Keys
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
* Rutger Ozinga: For the NPDB Inchi-keys and support with my thesis
* Michelle Schorn: For the extended MIBiG SMILES file.

----------------------------------------------------------------------------------------------------------------------------------------
## Explanation of Scripts

### eNPDB.py
This is the main script that runs the pipeline and in which the other scripts are used.
It is seperated into 7 steps:
1. Retrieving a list of the present structure identifiers from the SQL database. This list is used by the other scripts.
2. Load a file with (molconvert) inchi-keys for each identifier and add them to the SQL database.
3. Combine a split inchi-key back into a single one. (see explanation of Natural_Product_Structure.sqlite)
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
This scripts has 2 functions, on for step 2 and one for 3.
InsertIntoSQL is meant to take the inchi-keys from a file (all_input_structures_neutralized_full_dataFile.txt) and add them to the sqlite database.
CombineInchiKeys is used because my version of the starting SQL database has a version of the inchi-key that is split up (see explanation of file). This merges the two parts of the inchi-key and adds the necessary charge flag that it takes from the molconvert inchi-key added in step 2.


### ClassifyMibigTsv.py

### MIBiGToSQL4.py

### Run_pyclassyfire4.py


## Explanation of Files

### Natural_Product_Structure.sqlite

### all_input_structures_neutralized_full_dataFile.txt

### All_MIBiG_compounds_with_SMILES_and_PMID_MAS.txt
