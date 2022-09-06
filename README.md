# gMetaDataParse
## Extracts information from metadata_sqlite_db and the corresponding content_cache folder. Both artifacts of Google Drive for Desktop
Parsing the database and matching a file in the content_cache folder if provided and a file is still in cache
Offers json and csv export as well as a GUI.

## Usage
Option | Explanation
--- | ---
-f \<FILE\>, --file \<FILE\> | Path (relative or absolute) to the metadata_sqlite_db file. Example: C:\Data\metadata_sqlite_db
-d \<DIRECTORY\>, --directory \<DIRECTORY\> | Path (relative or absolute) to directory containing the cache. Example: C:\Data\content_cache
-o \<DIRECTORY\>, --output \<DIRECTORY\> | Path (relative or absolute) to directory were the output shoudl be written to. Example: C:\Data 
-j \<FILE\>, --json \<FILE\> | Filename for JSON output. Example: res.json
-c \<FILE\>, --csv \<FILE\> | Filename for CSV output. Example: res.csv
-v, --verbose | Increase output verbosity 
-g, --gui | Start GUI shown reconstruced directory tree with selected informaiton. If you want to use this function tkinter needs to be installed. 


## GUI
Entries were a matching file found in the content_cache are marked in green color.
If an entry is marked as trashed, it is marked in red.
The node "NO_PARENT_ITME_IN_ITEMS_TABEL" is a node added by pMetaDataParse. It is used to sort the items where no parent could be found in the itmes table. It is NOT an entry present in the metadata_sqlite_db file.!


## Requirements
See requirements.txt. 
To install on linux run: apt install -y python3-pip; apt install python3-tk; pip3 install -r requirements.txt 
To install on windows: install pip3; open PowerShell and run pip3 install -r requirements.txt

## Examples
```
# parse metadat_sqlite_db and the content cache folder, creating a csv file and a json file in the current directory
python3 ./gMetaDataParse.py -f ./gMetaDataParse.py -f .\metadata_sqlite_db -d .\content_cache\ -c res.csv -j res.json

# parse metadat_sqlite_db and the content cache folder, creating a csv file and a json file in the current directory AND lunch the GUI
python3 ./gMetaDataParse.py -f ./gMetaDataParse.py -f .\metadata_sqlite_db -d .\content_cache\ -c res.csv -j res.json -g

# parse metadat_sqlite_db and the content cache folder, starting the GUI showing the results
python3 ./gMetaDataParse.py -f ./gMetaDataParse.py -f .\metadata_sqlite_db -d .\content_cache\ -g

# starting the GUI, select metadata_sqlite_db and content_cache folder in the GUI
python3 ./gMetaDataParse.py 
```

## Limitations
If you review the code you will see a few things:
a) I'm not a GUI person and neither a person that likes to develop a GUI application. You will easily see this in the code; I still decided to offer write a very basic one.
b) The tool was basically done in the command line version, than I added the GUI on top. I might rewrite this somethimes in the future. Still I wanted to release, so the tool can be used.

## Author
* Twitter: [@b00010111](https://twitter.com/b00010111)
* Blog: https://00010111.at/

## License
* Free to use, reuse and redistribute for everyone.
* No Limitations.
* Of course attribution is always welcome but not mandatory.

## Bugs, Discussions, Feature requests, contact
* Still need to complete the description of each of the fields extracted and implement the function to print it.
* open an issue
* contact me via twitter

## further reading


## Change History
 * Version 0.0500:
    * initial release
