import os
import re
import json
import sqlite3
import pandas as pd


def load_file(filepath: str) -> str | None:
    """Load file contents safely."""
    try:
        with open(filepath, 'r', encoding='latin1') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None


def parse_abc_data(abc_text: str) -> list[dict]:
    """Split an ABC file into tunes and parse each one."""
    tune_blocks = re.split(r'\n\s*\n(?=X:)', abc_text)
    return [_parse_single_tune(block.splitlines()) for block in tune_blocks if block.strip()]


def _parse_single_tune(lines: list[str]) -> dict:
    """Parse a single tune block."""
    tune = {}
    notation = []

    for line in (line.strip() for line in lines):
        if not line or line.startswith('%'):
            continue

        header_match = re.match(r"^([A-Z]):(.*)", line)
        if header_match:
            key, value = header_match.groups()
            value = value.strip()

            if key in tune:
                # Convert duplicate values into list
                if isinstance(tune[key], list):
                    tune[key].append(value)
                else:
                    tune[key] = [tune[key], value]
            else:
                tune[key] = value
        else:
            notation.append(line)

    tune["music"] = "\n".join(notation)
    return tune


def gather_tunes(base_folder: str) -> list[dict]:
    """Recursively scan folders and parse ABC files."""
    all_tunes = []

    for dirpath, _, filenames in os.walk(base_folder):
        folder_name = os.path.basename(dirpath)

        # Expect folder names to be numbers representing book number
        if not folder_name.isdigit():
            continue

        book_number = int(folder_name)

        for filename in filenames:
            if filename.endswith(".abc"):
                path = os.path.join(dirpath, filename)
                content = load_file(path)
                if content:
                    tunes = parse_abc_data(content)
                    for tune in tunes:
                        tune["source_file"] = filename
                        tune["book_number"] = book_number
                    all_tunes.extend(tunes)

    print(f"Parsed {len(all_tunes)} tunes")
    return all_tunes


def create_database(db_filename: str, base_folder: str):
    """Process ABC files and store them in SQLite."""
    tunes = gather_tunes(base_folder)
    df = pd.DataFrame(tunes)

    # Convert list values to JSON strings
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(json.dumps)

    conn = sqlite3.connect(db_filename)
    df.to_sql("tunes", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Database created: {db_filename}, total tunes: {len(df)}")


def load_dataframe(db_filename: str) -> pd.DataFrame:
    """Load tunes table from SQLite into pandas DataFrame."""
    conn = sqlite3.connect(db_filename)
    df = pd.read_sql("SELECT * FROM tunes", conn)
    conn.close()
    return df


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abc_folder = os.path.join(script_dir, "..", "abc_books")
    db_path = os.path.join(script_dir, "tunes.db")

    create_database(db_path, abc_folder)

    # Load DB into DataFrame after building it
    df_loaded = load_dataframe(db_path)
    print(df_loaded.head())
    print("Loaded", len(df_loaded), "tunes into DataFrame")
