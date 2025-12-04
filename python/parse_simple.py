import os
import re
import pandas as pd
import json
import sqlite3

# Loads a file and returns its content as a string
def load_file(path):
    try:
        with open(path, "r", encoding="latin1") as f:
            return f.read()
    except:
        print(f"could not open file", path)
        return "" # return empty string if something goes wrong

# splits the abc text into separate tunes based on blank lines before X:
def split_tunes(abc_text):
    parts = re.split("(\n\s*\nX:.*)", abc_text)
    tunes = []
    for p in parts:
        tunes.append(read_one_tune(p.strip())) # parse each tune
    return tunes

# reads one tune and returns a dict with headers and music
def read_one_tune(lines):
    tune = {}
    lines = lines.split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("%"): # skip empty lines or comments
            continue

        # check if line is a header like T: or M:
        if len(line) > 2 and line[1] == ":" and line[0].isalpha():
            key = line[0].upper() # make uppercase so headers are consistent
            value = line[2:].strip()
            
            # if header already exists, turn it into a list
            if key in tune:
                if isinstance(tune[key], list):
                    tune[key].append(value)
                else:
                    tune[key] = [tune[key], value]
            else:
                tune[key] = value
        else:
            # everything else is music
            if "music" not in tune:
                tune["music"] = []
            tune["music"].append(line)

    if "music" in tune:
        tune["music"] = "".join(tune["music"]) # join music lines into one string
    return tune

# goes through all numbered folders and reads all abc files
def read_all_abc(folder):
    tunes = []

    for folder_path, sub, files in os.walk(folder):
        folder_name = os.path.basename(folder_path)

        if not folder_name.isdigit(): # skip folders that are not numbers
            continue
        
        book_num = int(folder_name)

        for file in files:
            if file.endswith(".abc"): # only look at abc files
                fp = os.path.join(folder_path, file)
                text = load_file(fp)
                
                if text:
                    found = split_tunes(text)
                    for t in found:
                        t["FILENAME"] = file # save the filename
                        t["BOOK_NUM"] = book_num # save the book number
                        tunes.append(t)
    
    print(f"total tunes:", len(tunes)) # print how many tunes we got
    return tunes

# create the sqlite database from all tunes
def create_database(dbname, folder):
    tunes = read_all_abc(folder)
    df = pd.DataFrame(tunes) # convert to pandas dataframe

    # convert lists to json strings so sqlite can store them
    for col in df.columns:
        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

    # clean column names so sqlite doesnt complain
    new_cols = []
    seen = set()
    for col in df.columns:
        name = col.strip().replace(" ", "_") # replace colon with underscore
        
        if not name:
            name = "unknown"

        name = name.lower() # make all lowercase

        if name[0].isdigit(): # if name starts with number, add prefix
            name = "col_" + name
        
        # make sure all column names are unique
        original = name
        i = 1
        while name in seen:
            name = f"{original}_{i}"
            i += 1
        
        seen.add(name)
        new_cols.append(name)

    df.columns = new_cols # rename columns
    
    conn = sqlite3.connect(dbname) # connect to sqlite
    df.to_sql("tunes", conn, if_exists="replace", index=False) # save df to db
    conn.close() # close connection

    print(f"database created", dbname) # confirm db created

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)) # get current folder
    abc_folder = os.path.join(here, "..", "abc books") # folder with abc books
    dbfile = os.path.join(here, "tunes.db") # path for sqlite db
    
    create_database(dbfile, abc_folder) # run the whole thing