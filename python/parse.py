import os
import re
import pprint
import pandas as pd

def parse_abc_data(abc_text):
    if not abc_text:
        return []
    tune_blocks = re.split(r'\n\s*\n(?=X:)', abc_text)
    parsed_tunes = []
    for block in tune_blocks:
        if block.strip():
            tune_dict = _parse_single_tune(block.strip().split('\n'))
            parsed_tunes.append(tune_dict)
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

def load(filepath):
    try:
        with open(filepath, 'r', encoding='latin1') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"ERROR: An error occurred while reading {filepath}: {e}")
        return None

def process_all_abc_files(base_folder):
    all_tunes = []
    file_count = 0

    print(f"Starting to search for .abc files in '{base_folder}'...")

    for dirpath, _, filenames in os.walk(base_folder):
        for filename in filenames:
            if filename.endswith('.abc'):
                file_path = os.path.join(dirpath, filename)
                print(f"Processing file: {filename}")
                
                abc_text = load(file_path)
                
                if abc_text:
                    tunes_from_file = parse_abc_data(abc_text)
                    
                    for tune in tunes_from_file:
                        tune['source_file'] = filename
                    
                    all_tunes.extend(tunes_from_file)
                    file_count += 1

    print(f"\nProcessing complete.")
    print(f"Found and parsed {len(all_tunes)} tunes from {file_count} files.")
    return all_tunes

if __name__ == "__main__":
    abc_root_folder = '../abc_books'
    
    all_parsed_data = process_all_abc_files(abc_root_folder)
    
    if all_parsed_data:
        print("\n---First tune parsed ---")
        pprint.pprint(all_parsed_data[0])
        
        print("\n--- Last tune parsed ---")
        pprint.pprint(all_parsed_data[-1])
        
        print("\n--- Converting to Pandas DataFrame ---")
        df = pd.DataFrame(all_parsed_data)
        
        print(df.head())
        
        print("\nDataFrame Info:")
        df.info()

        print("\n--- Example Analysis: Most Common Keys ---")
        if 'K' in df.columns:
            print(df['K'].value_counts().head(10))
        else:
            print("No 'K' (Key) field found in the data.")