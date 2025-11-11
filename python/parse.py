import pandas as pd
import os 

def load(word):
    
    try:
        with open(word, 'r', encoding='latin1') as f:
            text = f.read()
            print("Data loaded")
        return text
    except FileNotFoundError:
        print("Data not loaded")
        return None
    
def parse():

    text = load('abc_books/1/hnair0.abc')
    for word in text.split():
        cleaned_word = ''.join(char for char in word if char.isalnum())
        print(cleaned_word)

load('../abc_books/1/hnair0.abc')
parse()