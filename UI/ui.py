import py5
import sqlite3
import json
import re
import os

# --- Global variables to store the application's state ---
all_tunes_data = []
tunes_to_show_in_list = []
currently_selected_tune = None
list_scroll_position = 0
search_query = ""

def setup():
    """ This function runs only once at the start to load data and set up the window. """
    py5.size(1000, 700)
    py5.window_title("ABC Tune Viewer (DB Mode)")
    
    global all_tunes_data, tunes_to_show_in_list
    
    # --- Data Loading Directly From Database ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = os.path.join(script_dir, '..', 'python', 'tunes.db')

    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database_file)
        # This makes rows act like dictionaries, so we can access columns by name
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        # Get all data from the 'tunes' table
        cursor.execute("SELECT * FROM tunes")
        database_rows = cursor.fetchall()
        
        # --- Prepare Data for Display ---
        for row in database_rows:
            # Convert the database row to a standard Python dictionary
            tune = dict(row)
            
            # The database stores lists as JSON text (e.g., "['Title 1', 'Title 2']")
            # We need to convert it back.
            title_from_db = tune.get('T', 'Untitled')
            if isinstance(title_from_db, str) and title_from_db.startswith('['):
                try:
                    title_list = json.loads(title_from_db)
                    tune['display_title'] = title_list[0] # Just show the first title
                except:
                    tune['display_title'] = title_from_db # If parsing fails, show the raw text
            else:
                tune['display_title'] = title_from_db

            # Create numerical data for drawing the melody graph
            note_values = []
            music_text = tune.get('music', '')
            found_notes = re.findall(r"([_=^]?[A-Ga-g][,']*)", music_text)
            for note in found_notes:
                value = "CDEFGABcdefgab".find(note[-1])
                if value != -1:
                    if "'" in note: value += 7
                    if "," in note: value -= 7
                    note_values.append(value)
            tune['graph_data'] = note_values

            all_tunes_data.append(tune)
            
        connection.close()
        print(f"Successfully loaded {len(all_tunes_data)} tunes from the database.")

    except Exception as e:
        print(f"An error occurred while reading the database: {e}")

    # At the beginning, the list we show is all the tunes.
    tunes_to_show_in_list = all_tunes_data

def draw():
    """ This function runs in a loop to draw everything on the screen. """
    py5.background(30)
    
    # --- Sidebar ---
    py5.fill(40); py5.no_stroke(); py5.rect(0, 0, 300, py5.height)
    
    # Search Box
    py5.fill(20); py5.rect(10, 10, 280, 40)
    py5.fill(220); py5.text_size(16)
    cursor = "_" if (py5.frame_count % 60 < 30) else ""
    py5.text("Search: " + search_query + cursor, 20, 38)

    # List of Tunes
    for i, tune in enumerate(tunes_to_show_in_list):
        y = 60 + (i * 30) - list_scroll_position
        if y > 50 and y < py5.height:
            if tune == currently_selected_tune: py5.fill(100, 150, 255)
            else: py5.fill(220)
            py5.text(tune.get('display_title', 'Untitled')[:35], 15, y)

    # --- Main Content ---
    if currently_selected_tune is None:
        py5.fill(150); py5.text_size(20)
        py5.text("Select a tune from the list", 450, 350)
    else:
        x = 320
        # Title and Info
        py5.fill(255); py5.text_size(28)
        py5.text(currently_selected_tune.get('display_title', 'Untitled'), x, 50)
        py5.fill(200); py5.text_size(14)
        info = "Key: " + currently_selected_tune.get('K', '?') + " | Book: " + str(currently_selected_tune.get('book_number', '?'))
        py5.text(info, x, 80)
        
        # Melody Graph
        py5.no_fill(); py5.stroke(100); py5.rect(x, 130, 650, 150)
        notes = currently_selected_tune['graph_data']
        if len(notes) > 1:
            py5.stroke(100, 200, 255); py5.stroke_weight(2)
            py5.begin_shape()
            for i, note_val in enumerate(notes):
                graph_x = x + (i * (650.0 / len(notes)))
                graph_y = 250 - (note_val * 5)
                py5.vertex(graph_x, graph_y)
            py5.end_shape()

        # Raw Music Text
        py5.fill(200); py5.text("Raw Music Data:", x, 320)
        py5.text(currently_selected_tune.get('music', ''), x + 10, 350)

def mouse_clicked(e):
    global currently_selected_tune
    if py5.mouse_x < 300 and py5.mouse_y > 60:
        index = int((py5.mouse_y - 60 + list_scroll_position) / 30)
        if 0 <= index < len(tunes_to_show_in_list):
            currently_selected_tune = tunes_to_show_in_list[index]

def mouse_wheel(e):
    global list_scroll_position
    list_scroll_position += e.get_count() * 20
    if list_scroll_position < 0: list_scroll_position = 0

def key_typed(e):
    global search_query, tunes_to_show_in_list, list_scroll_position
    key = py5.key
    if key == py5.BACKSPACE: search_query = search_query[:-1]
    elif str(key).isprintable(): search_query += str(key)
    
    new_filtered_list = []
    search_term = search_query.lower()
    for tune in all_tunes_data:
        if search_term in tune.get('display_title', '').lower():
            new_filtered_list.append(tune)
    tunes_to_show_in_list = new_filtered_list
    list_scroll_position = 0

if __name__ == "__main__":
    py5.run_sketch()