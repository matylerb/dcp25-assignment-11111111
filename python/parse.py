import pandas as pd


data = None

def load(word):
    global data


    try:
        with open(word, 'r', encoding='latin1') as f:
            text = f.read()
            print("Data loaded")
        return text
    except FileNotFoundError:
        print("Data not loaded")
        return None
    
load(/abc_books)