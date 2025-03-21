# gMetaDataParse
## Extracts information from metadata_sqlite_db and the corresponding content_cache folder. Both artifacts of Google Drive for Desktop
Parsing the database and matching a file to the filename in the content_cache folder, if provided and the file is still in cache.
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
-g, --gui | Start GUI shown reconstruced directory tree with selected information. You need to use the -f option in combination with -g. To start just the GUI run without commands 


## GUI
Entries were a matching file found in the content_cache are marked in green color.
If an entry is marked as trashed, it is marked in red.
The node "NO_PARENT_ITME_IN_ITEMS_TABEL" is a node added by pMetaDataParse. It is used to sort the items where no parent could be found in the itmes table. It is NOT an entry present in the metadata_sqlite_db file.!

I further created an executable with auto-py-to-exe, this executable will open the GUI and you can select "content_cache" and "metadat_sqlite_db" via the menue. Click afterwards click reload.

One thing on the GUI: I will not show all data extracted, it is more to visualize things, focus on some important and have a more easy access to the tool. If you want to see everything that gMetaDataParse extracts, use the --csv or --json output in the command line.

## Requirements
* See requirements.txt. 
* To install on linux run (tested on fresh Ubuntu 22 install): apt install -y python3-pip; apt install -y python3-tk; pip3 install -r requirements.txt 
* To install on windows: install pip3; open PowerShell and run pip3 install -r requirements.txt OR you use the provided executable

## Examples
```
# parse metadat_sqlite_db and the content cache folder, creating a csv file and a json file in the current directory
python3 ./gMetaDataParse.py -f .\metadata_sqlite_db -d .\content_cache\ -c res.csv -j res.json

# parse metadat_sqlite_db and the content cache folder, creating a csv file and a json file in the current directory AND lunch the GUI
python3 ./gMetaDataParse.py -f .\metadata_sqlite_db -d .\content_cache\ -c res.csv -j res.json -g

# parse metadat_sqlite_db and the content cache folder, starting the GUI showing the results
python3 ./gMetaDataParse.py -f .\metadata_sqlite_db -d .\content_cache\ -g

# starting the GUI, select metadata_sqlite_db and content_cache folder in the GUI
python3 ./gMetaDataParse.py 
```

## Limitations
* If you review the code you will see a few things:
* I'm not a GUI person and neither a person that likes to develop a GUI application. You will easily see this in the code; I still decided to offer write a very basic one.
* The tool was basically done in the command line version, than I added the GUI on top. I might rewrite this in the future. Still I wanted to release, so the tool can be used.

## Author
* Mastodon: [@b00010111](https://ioc.exchange/@b00010111)
* Blog: https://00010111.at/
* Twitter: [@b00010111](https://twitter.com/b00010111)

## License
* Free to use, reuse and redistribute for everyone.
* No Limitations.
* Of course attribution is always welcome but not mandatory.

## Bugs, Discussions, Feature requests, contact
* Still need to complete the description of each of the fields extracted and implement the function to print it.
* open an issue
* contact me via Mastodon
* (reaching out via Twitter doesn't really work well anymore...sorry)

## further reading


## Change History
 * Version 0.0502:
    * Fix issue 1
	  * If neither json,csv,gui or verbose is choosen as output, gMetaDataParse will fall back to write csv output to local directory with a filename like: %Y%m%d_%H%M%S_output.csv
	* improved error handling if database or cache dir are not found
 * Version 0.0501:
    * Bug fix
	* GUI was showing wrong data in 'Found in cache dir' column for deleted items. Thanks to @chadtilbury for pointing out the issue.
 * Version 0.0500:
    * initial release
