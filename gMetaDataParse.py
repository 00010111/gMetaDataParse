#!/usb/bin/env python3
# -*- coding: utf-8 -*-

# Author: twitter: @b00010111
#PowerShell example python3.9.exe .\gMetaDataParse.py -f .\test_data\1\metadata_sqlite_db -d .\test_data\1\content_cache\ -c res.csv -j res.json -g

import argparse
from pathlib import Path
import sqlite3
import os
import blackboxprotobuf
from datetime import datetime
import json,csv

import tkinter as tk

verbose = False
tree = None
Output = None
version_string = "0.0500" 
entries = {}
metadata_file = ''
cache_dir = ''
db_path = ''

#code to select the cache folder via the gui
def select_folder(title="Select folder", folder=".", master=None):
    global cache_dir
    global db_path
    from tkinter import filedialog
    cache_dir = filedialog.askdirectory(title=title, initialdir=folder, parent=None if master is None else master.tk)
#    print (cache_dir)
    #test code to delete an item and see if refresh creates a new correct treeview
    #tree.delete(202)
    #file_field has three lines, add to last line click refresh
    # file_field is a global field, we can use it directly
    # empty file_filed, set value for both, change bg color add "refresh"
    file_field.delete(1.0,tk.END)
    file_field.insert(1.0,"After you have seleced a new cache directory and database, click RELOAD!!\n")
    file_field.insert(1.0,"Path to database:" + str(db_path) +"\n")
    file_field.insert(1.0,"Path to cache dir:" + str(cache_dir)+"\n")
    file_field.config(background='#ff6347')


    
def onOpen(title="Open metadata_sql", folder=".", master=None):
    global metadata_file
    global db_path
    global cache_dir
    from tkinter import filedialog
    metadata_file = filedialog.askopenfilename(title=title, initialdir=folder, parent=None if master is None else master.tk)
    db_path = metadata_file
#    print (metadata_file)
    #file_field has three lines, add to last line click refresh
    # file_field is a global field, we can use it directly
    # empty file_filed,  add "refresh", add value for both, change bg color
    file_field.delete(1.0,tk.END)
    file_field.insert(1.0,"After you have seleced a new cache directory and database, click RELOAD!!\n")
    file_field.insert(1.0,"Path to database:" + str(db_path) +"\n")
    file_field.insert(1.0,"Path to cache dir:" + str(cache_dir)+"\n")
    file_field.config(background='#ff6347')
    
def refresh():
    global cache_dir
    global db_path
    global metadata_file
    # we can directly use tree here to delete and add things to the table view.
    for item in tree.get_children():
        tree.delete(item)
    # we need to call parse db and later repeat the code that addes the results to the table and we shoud be good to go.
    #connect to db again to get parent to child sorted by item_stable_id
    if os.path.isfile(db_path) == False:
        if verbose:
            print("could not find file: " + db_path)
        exit(1)
    conn = sqlite3.connect(db_path)
    if verbose:
        print("database connected\ndatabase path: " + str(db_path))
    # get parent_child relationsships
    cursor = conn.execute("SELECT stable_parents.item_stable_id,stable_parents.parent_stable_id from stable_parents order by stable_parents.item_stable_id;")
    #index for pc2 is item_stable_id
    p2c = {}
    for row in cursor:
        stable_id = row[0]
        p2c[stable_id]= row[1]
    #get max number of items
    max_items = 0
    cursor = conn.execute("SELECT MAX(stable_id) from items;")
    max_items = cursor.fetchone()[0] + 100
    
    refresh_entries = parseDB(db_path,cache_dir)
    for k,v in refresh_entries.items():
        if len(v.get('found_cache_files',''))> 0:
            tree.insert('','end',text=v['items.local_title'], values=(v.get('items.file_size',''),v.get('items.modified_date',''),v.get('items.viewed_by_me_date',''),v.get('items.shared_with_me_date',''),v.get('cache_filename',''),'Yes',v.get('items.trashed',''),v.get('items.is_owner',''),v.get('items.is_folder',''),v.get('items.mime_type',''),v.get('item_properties.key.modified-date',''),v.get('item_properties.key.local-content-modified-date','')),iid=k,tags = ('cache_file',))
        elif v.get('items.trashed','0') != 0:
            tree.insert('','end',text=v['items.local_title'], values=(v.get('items.file_size',''),v.get('items.modified_date',''),v.get('items.viewed_by_me_date',''),v.get('items.shared_with_me_date',''),v.get('cache_filename',''),'Yes',v.get('items.trashed',''),v.get('items.is_owner',''),v.get('items.is_folder',''),v.get('items.mime_type',''),v.get('item_properties.key.modified-date',''),v.get('item_properties.key.local-content-modified-date','')),iid=k,tags = ('trashed_file',))
        else:
            tree.insert('','end',text=v['items.local_title'], values=(v.get('items.file_size',''),v.get('items.modified_date',''),v.get('items.viewed_by_me_date',''),v.get('items.shared_with_me_date',''),v.get('cache_filename',''),'No',v.get('items.trashed',''),v.get('items.is_owner',''),v.get('items.is_folder',''),v.get('items.mime_type',''),v.get('item_properties.key.modified-date',''),v.get('item_properties.key.local-content-modified-date','')),iid=k)
    ###USE stable_id as iid!!!
    #insert NO_Parent_ITEM_in items_table 
    tree.insert('','end',text='NO_PARENT_ITEM_IN_ITEMS_TABLE', iid=max_items)
    #sort the tree
    for k,v in p2c.items():
        #print(entries.get(k,None))
        #print(entries.get(v,None)) 
        if entries.get(v,None) != None:
            tree.move(k,v,'end')
            #print("NP PARENT ITEM for k: " + str(k))
        else:
            tree.move(k,max_items,'end')
    tree.tag_configure('cache_file', background='#327043')
    tree.tag_configure('trashed_file', background='#ff0800')
    # file_field is a global field, we can use it directly
    # empty file_filed,  add "refresh", add value for both, change bg color
    file_field.delete(1.0,tk.END)
    file_field.insert(1.0,"Path to database:" + str(db_path) +"\n")
    file_field.insert(1.0,"Path to cache dir:" + str(cache_dir)+"\n")
    file_field.config(background="light cyan")

#callback for GUI if an entry is selected.
#this method is responsible for the text area to be updated with information for the selected item
def selectItem(a):
    global entries
    curItem = tree.focus()
    Output.delete(1.0,"end")
    #stable_id is used as iid for the tree, further it is the key used in entires
    selected_iid = tree.selection()
    selected_entry = entries.get(int(selected_iid[0]))
 #   for k,v in selected_entry.items():
 #       Output.insert(1.0,str(k) + " : " + str(v)+"\n")
    if selected_entry != None:
        Output.insert(1.0,"is Owner : " + str(selected_entry.get('items.is_owner','-')) +"\n")
        Output.insert(1.0,"is Folder : " + str(selected_entry.get('items.is_folder','-')) +"\n")
        Output.insert(1.0,"Trashed : " + str(selected_entry.get('items.trashed','-')) +"\n")
        Output.insert(1.0,"MIME type : " + str(selected_entry.get('items.mime_type','-')) +"\n")
        Output.insert(1.0,"Size : " + str(selected_entry.get('items.file_size','-')) +"\n")
        Output.insert(1.0,"Mod Date of local content (item_properties) : " + str(selected_entry.get('item_properties.key.local-content-modified-date','-')) +"\n")
        Output.insert(1.0,"Mod Date (item_properties) : " + str(selected_entry.get('item_properties.key.modified-date','-')) +"\n")
        Output.insert(1.0,"Shared Date : " + str(selected_entry.get('items.shared_with_me_date','-')) +"\n")
        Output.insert(1.0,"Viewed Date : " + str(selected_entry.get('items.viewed_by_me_date','-')) +"\n")
        Output.insert(1.0,"Modifed Date : " + str(selected_entry.get('items.modified_date','-')) +"\n")
        for s in selected_entry.get('found_cache_files','-'):
            Output.insert(1.0,"Cache Dir File Path : " + s +"\n")
        Output.insert(1.0,"Local Filename : " + str(selected_entry.get('item_properties.key.local-title','-')) +"\n")
        Output.insert(1.0,"Stable Id : " + str(selected_entry.get('items.stable_id','-')) +"\n")


#Method to reconstruct the local file path, runs recusivley per searchID until no more parent found
#Parameter: searchID -> stable_ID to find the parent for
#Parameter: entry_object -> the parses item we want to reconstruct the path for
#Parameter: entries -> dict containng all parsed items
def construct_path(searchID,entry_object,entries):
    parent = None
    parent_object = entries.get(searchID,None)
    if parent_object != None:
        parent = parent_object.get('parent_stable_id',None)
    if parent != None:
        #get local_title of parent from entries object (contains all parsed items)
        if entries.get(parent,None) != None:
            parent_local_title = entries.get(parent,'').get('items.local_title','')
        else:
            parent_local_title = 'No_Local_Title'
        #add parent path to the File_Path of the entry_object
        entry_object['File_Path'] = parent_local_title + '/' + entry_object.get('File_Path','')
        #recursive call with parent id to finsh up the entry_opject until no further parent is found
        construct_path(parent,entry_object,entries)

#Method to parse metadata_sqlite_db and search for files in local cache path if given
#Parameter: db_path Path to the metadata_sqlite_db file
#Parameter: s_path_local_cache local path to the cache folder is located
#Return: entries dictionary containing the parsed streemfs.db entries and the enritchment fields added
def parseDB(db_path,s_path_local_cache):
    global verbose
    global entries
    if os.path.isfile(db_path) == False:
        if verbose:
            print("could not find file: " + db_path)
        exit(1)
    entries = {}
    types = {}
    conn = sqlite3.connect(db_path)
    if verbose:
        print("database connected\ndatabase path: " + str(db_path))
        
    # get parent_child relationsships
    cursor = conn.execute("SELECT stable_parents.item_stable_id,stable_parents.parent_stable_id from stable_parents;")
    #index for pc2 is item_stable_id
    p2c = {}
    for row in cursor:
        stable_id = row[0]
        p2c[stable_id]= row[1]
    #rows are tuples
    cursor = conn.execute("SELECT items.stable_id,items.trashed, items.is_owner, items.mime_type, items.is_folder, items.modified_date, items.viewed_by_me_date, items.local_title, items.file_size, items.shared_with_me_date from items;")
    for row in cursor:
        stable_id = row[0]
        entries[stable_id] = {'items.stable_id':row[0],'items.trashed':row[1],'items.is_owner':row[2], 'items.mime_type':row[3], 'items.is_folder':row[4], 'items.modified_date':row[5], 'items.viewed_by_me_date':row[6], 'items.local_title':row[7], 'items.file_size':row[8], 'items.shared_with_me_date':row[9]}
    
    ##loop over entries and get item_properties, parse out cache file name, parse dates and set parent_stable_id
    for k,entry in entries.items():
        entry['parent_stable_id'] = p2c.get(k,'')
        #use k to select the items_properties
        cursor = conn.execute("Select item_properties.key,item_properties.value,item_properties.value_type from item_properties where item_properties.item_stable_id = ?;", (k,))
        #enrich row
        for row in cursor:
            #print(row)
            fieldname = 'item_properties.key.' + row[0]
            
            #print (str(row[0]))
            #this works for blog
            if row[0] == 'content-entry':
                # we can use the output from the db directly to decode the protobuf, it is already binary
                values, _ = blackboxprotobuf.decode_message(row[1], types)
                fieldname += '_parsed'
                entry[fieldname] = str(values)
                entry['cache_filename'] = str(values.get('1'))
                #print(values)
                
            else:
                entry[fieldname] = str(row[1])
                #print(row[1])
        ##parse dates
        if entry.get('items.modified_date',0) != 0:
            #Unix: Millisecond value, need /1000 for parsing
            dt_object = datetime.utcfromtimestamp(entry.get('items.modified_date',None)/1000)
            entry['items.modified_date'] = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if entry.get('items.viewed_by_me_date',0) != 0:
            #Unix: Millisecond value, need /1000 for parsing
            dt_object = datetime.utcfromtimestamp(entry.get('items.viewed_by_me_date',None)/1000)
            entry['items.viewed_by_me_date'] = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if entry.get('items.shared_with_me_date',0) != 0:
            #Unix: Millisecond value, need /1000 for parsing
            dt_object = datetime.utcfromtimestamp(entry.get('items.shared_with_me_date',None)/1000)
            entry['items.shared_with_me_date'] = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if entry.get('item_properties.key.local-content-modified-date',0) != 0:
            #Unix: Millisecond value, need /1000 for parsing
            dt_object = datetime.utcfromtimestamp(int(entry.get('item_properties.key.local-content-modified-date',None))/1000)
            entry['item_properties.key.local-content-modified-date'] = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if entry.get('item_properties.key.modified-date',0) != 0:
            #Unix: Millisecond value, need /1000 for parsing
            dt_object = datetime.utcfromtimestamp(int(entry.get('item_properties.key.modified-date',None))/1000)
            entry['item_properties.key.modified-date'] = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        #item_properties.key.modified-date
        #get cache path candidates
        if (entry.get('cache_filename',None) != None) and (not s_path_local_cache is None):
        #if entry.get('cache_filename',None) != None:
            s_g_files = []
            for g_file in Path(s_path_local_cache).rglob(entry.get('cache_filename')):
                #s_g_files.append(os.path.relpath(g_file))
                s_g_files.append(str(g_file))
            
            entry['found_cache_files'] = s_g_files
        construct_path(k,entry,entries)
        #print(entry)
#items.shared_with_me_date            
        #print(entry)
    return entries

#Function to write one instance of parsed and enritched metadata_sqlite_db
#Parameter: entries dict containing on parsed and enritched metadata_sqlite_db
#Parameter: outputdir file will be written to this dir, if this parameter is empty the file will be written in current working directory
#Parameter: filename output file name
def writeJSON(entries,outputdir,filename):
    global verbose
    filename = os.path.join(outputdir, filename)
    jsonfile = open(filename,'w')
    if os.path.isdir(outputdir) == False:
        print("Output directory does not exist, exiting")
        exit(1)
    if verbose:
        print("Writing json resultfile to:")
        print(os.path.abspath(jsonfile.name))
    for k,v in entries.items():
        json.dump(v, jsonfile)

#Function to write one instance of parsed and enritched metadata_sqlite_db
#Parameter: entries dict containing on parsed and enritched metadata_sqlite_db
#Parameter: outputdir file will be written to this dir, if this parameter is empty the file will be written in current working directory
#Parameter: filename output file name
def writeCSV(entries,outputdir,filename):
    global verbose
    filename = os.path.join(outputdir, filename)
    csvfile = open(filename,'w',encoding="utf-8",newline='')
    if os.path.isdir(outputdir) == False:
        print("Output directory does not exist, exiting")
        exit(1)
    if verbose:
        print("Writing CSV resultfile to:")
        print(os.path.abspath(csvfile.name))
    l = []
    for k,v in entries.items():
        for i in v:
            l.append(i)
    csvHeaderList = list(set(l))
    csvwriter = csv.DictWriter(csvfile, delimiter=',', quotechar='\"', fieldnames=csvHeaderList)
    csvwriter.writeheader()
    for k,v in entries.items():
        csvwriter.writerow(v)
    csvfile.close()

#Function to load the gui.
# Parameter: entries fully parsed and enriched entires from metadata_sqlite_db
# Parameter: db_path path to metadata_sqlite_db
def lunchgui(entries,db_path):
    global verbose
    global tree
    global Output
    global file_field
    if not db_path is None:
        #connect to db again to get parent to child sorted by item_stable_id
        if os.path.isfile(db_path) == False:
            if verbose:
                print("could not find file: " + db_path)
            exit(1)
        conn = sqlite3.connect(db_path)
        if verbose:
                print("database connected\ndatabase path: " + str(db_path))

        # get parent_child relationsships
        cursor = conn.execute("SELECT stable_parents.item_stable_id,stable_parents.parent_stable_id from stable_parents order by stable_parents.item_stable_id;")
        #index for pc2 is item_stable_id
        p2c = {}
        for row in cursor:
            stable_id = row[0]
            p2c[stable_id]= row[1]
        #get max number of items
        max_items = 0
        cursor = conn.execute("SELECT MAX(stable_id) from items;")
        max_items = cursor.fetchone()[0] + 100
    
    import tkinter as tk
    from tkinter import ttk
    from tkinter import Text
    from tkinter.messagebox import showinfo 
    
    root = tk.Tk()
    root.resizable(width = 1, height = 1)
    root.title('gMetaDataParse - View')
    root.geometry('1600x800')
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open cache folder", command=select_folder)
    filemenu.add_command(label="Open database", command=onOpen)
    filemenu.add_command(label="Reload", command=refresh)
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)
    #adding field to contain info which files are set.
    file_field = Text(root, bg = "light cyan", height = 3,)
    file_field.insert(1.0,"Path to database:" + str(db_path) +"\n")
    file_field.insert(1.0,"Path to cache dir:" + str(cache_dir)+"\n")
    file_field.pack(fill=tk.X)
    #
    #tree = ttk.Treeview(root)
    tree = ttk.Treeview(root,selectmode='browse')
    #tree = ttk.Treeview(root,show='tree')
    #tree.grid()
    tree.pack(fill='both',expand=1)
    #tree.pack(fill=tk.X)

    Output = Text(root, bg = "light cyan", height = 15,)  
    Output.pack(fill=tk.X)

    
    treeScroll = ttk.Scrollbar(tree) 
    treeScroll.configure(command=tree.yview) 
    tree.configure(yscrollcommand=treeScroll.set) 
    treeScroll.pack(side= 'right', fill= 'both')    
    
#    outputScroll = ttk.Scrollbar(Output) 
#    outputScroll.pack(side= 'right',expand=0)    

    tree['columns'] = ('items.file_size', 'items.modified_date', 'items.viewed_by_me_date', 'items.shared_with_me_date','cache_filename','found_cache_files','items.trashed','items.is_owner','items.is_folder','items.mime_type','item_properties.key.modified-date','item_properties.key.local-content-modified-date' )
    tree.heading('items.file_size', text='Size')
    tree.heading('items.modified_date', text='Modifed Date')
    tree.heading('items.viewed_by_me_date', text='Viewed Date')
    tree.heading('items.shared_with_me_date', text='Shared Date')
    tree.heading('cache_filename', text='Cache file name')
    tree.heading('found_cache_files', text='Found in cache dir')
    tree.heading('items.trashed', text='trashed')
    tree.heading('items.is_owner', text='is_owner')
    tree.heading('items.is_folder', text='is_folder')
    tree.heading('items.mime_type', text='MIME type')
    tree.heading('item_properties.key.modified-date', text='item_props Mod Date')
    tree.heading('item_properties.key.local-content-modified-date', text='item_props Mod Date Local')

    tree.column('items.file_size',width=100, anchor='center')
    tree.column('items.modified_date',width=135, anchor='center')
    tree.column('items.viewed_by_me_date',width=135, anchor='center')
    tree.column('items.shared_with_me_date',width=135, anchor='center')
    tree.column('cache_filename',width=110, anchor='center')
    tree.column('items.trashed',width=50, stretch=tk.NO, anchor='center')
    tree.column('found_cache_files',width=120, stretch=tk.NO, anchor='center')
    tree.column('items.is_owner',width=60, stretch=tk.NO, anchor='center')
    tree.column('items.is_folder',width=60, stretch=tk.NO, anchor='center')
    tree.column('items.mime_type',width=100, anchor='center')
    tree.column('item_properties.key.modified-date',width=150, anchor='center')
    tree.column('item_properties.key.local-content-modified-date',width=250, anchor='center')
    
    tree.bind('<ButtonRelease-1>', selectItem)

    if not entries is None:
        
        for k,v in entries.items():
            if len(v.get('found_cache_files',''))> 0:
                tree.insert('','end',text=v['items.local_title'], values=(v.get('items.file_size',''),v.get('items.modified_date',''),v.get('items.viewed_by_me_date',''),v.get('items.shared_with_me_date',''),v.get('cache_filename',''),'Yes',v.get('items.trashed',''),v.get('items.is_owner',''),v.get('items.is_folder',''),v.get('items.mime_type',''),v.get('item_properties.key.modified-date',''),v.get('item_properties.key.local-content-modified-date','')),iid=k,tags = ('cache_file',))
            elif v.get('items.trashed','0') != 0:
                tree.insert('','end',text=v['items.local_title'], values=(v.get('items.file_size',''),v.get('items.modified_date',''),v.get('items.viewed_by_me_date',''),v.get('items.shared_with_me_date',''),v.get('cache_filename',''),'Yes',v.get('items.trashed',''),v.get('items.is_owner',''),v.get('items.is_folder',''),v.get('items.mime_type',''),v.get('item_properties.key.modified-date',''),v.get('item_properties.key.local-content-modified-date','')),iid=k,tags = ('trashed_file',))
            else:
                tree.insert('','end',text=v['items.local_title'], values=(v.get('items.file_size',''),v.get('items.modified_date',''),v.get('items.viewed_by_me_date',''),v.get('items.shared_with_me_date',''),v.get('cache_filename',''),'No',v.get('items.trashed',''),v.get('items.is_owner',''),v.get('items.is_folder',''),v.get('items.mime_type',''),v.get('item_properties.key.modified-date',''),v.get('item_properties.key.local-content-modified-date','')),iid=k)
        ###USE stable_id as iid!!!
        #insert NO_Parent_ITEM_in items_table 
        tree.insert('','end',text='NO_PARENT_ITEM_IN_ITEMS_TABLE', iid=max_items)
        #sort the tree
        for k,v in p2c.items():
            #print(entries.get(k,None))
            #print(entries.get(v,None)) 
            if entries.get(v,None) != None:
                tree.move(k,v,'end')
                #print("NP PARENT ITEM for k: " + str(k))
            else:
                tree.move(k,max_items,'end')
        tree.tag_configure('cache_file', background='#327043')
        tree.tag_configure('trashed_file', background='#ff0800')
    
    root.mainloop()    

#Function to print the explanation of the fields
#FIXME:need to be finished and implemented when/how to show it
def printDoc():
    print("Size: File size in bytes")
    print("Modified Date: Last modified time; timestamp begins at the time the file was first added to Google Drive, not original file modification time")
    print("Viewed Date: Time of last user interaction with the file. Can be set by activity other than viewing, such as copies or moves.")
    print("Shared Date: Time the user shared the data ")
    print("Cache file name: file name of cache file taken from items table")
    print("Found in cache dir: 1-> a corresponding file is found in the content cache folder. Mapping is done base on filename taken from database and searched in content cache.")
    print("trashed: 1-> file deleted")
    print("is_owner: 1-> User from which metadata_sqlite_db is taken is the owner of this file")
    print("is_folder: 1-> Folder; 0-> File")
    print("MIME type: MIME type of the file")
    print("item_props Mod Date: Modification time of the file reported from the local filesystem")
    print("item_props Mod Date local: FIXME")
    print("CSV & JSON only")
    print("FIXME, this still needs to be documented")

# start
parser = argparse.ArgumentParser(description='Process Google Drive for Desktop metadata_sqllite_db and the correspondig cache directory.')
#group = parser.add_mutually_exclusive_group()
parser.add_argument("-v", "--verbose", help="Increase output verbosity",action="store_true")
parser.add_argument("-f","--file", type=lambda p: Path(p).absolute(), help="Path (relative or absolute) to the metadata_sqlite_db file. Example: C:\Data\metadata_sqlite_db")
parser.add_argument("-d","--directory", type=lambda p: Path(p).absolute(), help="Path (relative or absolute) to directory containing the cache. Example: C:\Data\content_cache")
parser.add_argument("-o","--output", type=lambda p: Path(p).absolute(), help="Path (relative or absolute) to directory were the output shoudl be written to. Example: C:\Data")
parser.add_argument("-j","--json",help="Filename for JSON output. Example: res.json")
parser.add_argument("-c","--csv",help="Filename for CSV output. Example: res.csv")
parser.add_argument("-g","--gui",help="Start GUI shown reconstruced directory tree with selected information. You need to use the -f option in combination with -g. To start just the GUI run without commands",action="store_true")

args = parser.parse_args()

if args.verbose:
    print("gMetaDataParse Version: " + version_string)
    verbose = True

metadata_file = args.file
db_path = metadata_file
cache_dir = args.directory    

#print(len(args))
if not any(vars(args).values()):
#if not 1 > 1:
    #no args given
    #print("no args given")
    lunchgui(None,None)
elif args.gui and not db_path:
    print("If you use the -g,--gui option you need to provide the path to the metadata_sqlite_db file with the -f option. To start the GUI without choosing a file, run without any commandline option")
    exit(1)
else:
    res = parseDB(metadata_file,cache_dir)
    if args.output == None:
        args.output = '.'
    if args.json != None:
        writeJSON(res,args.output,args.json)
    if args.csv != None:
        writeCSV(res,args.output,args.csv)
    if args.verbose:
        for k,v in res.items():
            print(v)
    if args.gui:
        lunchgui(res,metadata_file)
    #Documentation: dates set to 0 means the database contained 0 aka no date
