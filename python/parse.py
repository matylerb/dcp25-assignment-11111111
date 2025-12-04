import os
import re
import pandas as pd
import json
import sqlite3

def load(filepath):
    try:
        with open(filepath, 'r', encoding='latin1') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found at {filepath}")
        return None

def parse_abc_data(abc_text):
    tune_blocks = re.split(r'\n\s*\n(?=X:)', abc_text)
    parsed_tunes = [
        _parse_single_tune(block.strip().split('\n'))
        for block in tune_blocks if block.strip()
    ]
    return parsed_tunes

def _parse_single_tune(tune_lines):
    tune_dict = {}
    music_notation = []
    
    for line in tune_lines:
        line = line.strip()
        if not line or line.startswith('%'): 
            continue
        
        if re.match(r"^[A-Z]:", line):
            key = line[0]
            value = line[2:].strip()
            
      
            if key in tune_dict:
                if isinstance(tune_dict[key], list):
                    tune_dict[key].append(value)
                else:
                    tune_dict[key] = [tune_dict[key], value]
            else:
                tune_dict[key] = value
        else:
            music_notation.append(line)

    tune_dict['music'] = '\n'.join(music_notation)
    return tune_dict

def process_all_abc_files(base_folder):
    all_tunes = []

    for dirpath, _, filenames in os.walk(base_folder):
        folder_name = os.path.basename(dirpath)
        
        # Only process folders that are numbered (based on your original logic)
        if not folder_name.isdigit():
            continue
            
        book_number = int(folder_name)
        
        for filename in filenames:
            if filename.endswith('.abc'):
                file_path = os.path.join(dirpath, filename)
                abc_text = load(file_path)
                if abc_text:
                    tunes_from_file = parse_abc_data(abc_text)
                    for tune in tunes_from_file:
                        tune['source_file'] = filename
                        tune['book_number'] = book_number
                    all_tunes.extend(tunes_from_file)
                    
    print(f"Found and parsed {len(all_tunes)} tunes.")
    return all_tunes

def setup_database(db_filename, base_folder):
    all_parsed_data = process_all_abc_files(base_folder)
    
    df = pd.DataFrame(all_parsed_data)

    # convert lists to json so sqlite can store them
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(json.dumps)
    
    # open sqlite connection
    conn = sqlite3.connect(db_filename)
    
    # write dataframe to sqlite
    df.to_sql('tunes', conn, if_exists='replace', index=False)
    
    # close connection
    conn.close()
    
    print(f"database created at {db_filename} with {len(df)} tunes")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abc_root_folder = os.path.join(script_dir, '..', 'abc_books')
    database_file = os.path.join(script_dir, 'tunes.db')
    
    setup_database(database_file, abc_root_folder)