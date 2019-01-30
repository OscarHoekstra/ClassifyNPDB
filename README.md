# Thesis_Bsc_Oscar

One Paragraph of project description goes here

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

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

No versioning was used for this project.

## Authors

* **Oscar Hoekstra** - *Construction of pipeline* - (https://github.com/OscarHoekstra)

See also the list of [contributors](https://github.com/OscarHoekstra/Thesis_Bsc_Oscar/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
