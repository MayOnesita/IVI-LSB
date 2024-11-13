import gspread
import tkinter as tk
from tkinter import filedialog
import json
from google.oauth2.service_account import Credentials
from database import clean_database, remove_empty_scripts

SPREADSHEET_NAME = 'Categorizacion LSB' 
SHEET_NAME = 'Glosario v3'
SERVICE_ACCOUNT_FILE = 'COMPILER/client.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
          'https://www.googleapis.com/auth/drive.readonly']

def fetch_database():
    # Authorize and create a client to interact with the Google Sheets API
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)

    # Open the Google Sheet
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(SHEET_NAME)
    return(worksheet.get_all_values())

def export_dictionnary_json(dictionnary, json_path):
    with open(json_path, 'w') as f:
        json.dump(dictionnary, f, indent=4)

def export_animations_json(dictionnary):
    formatted_data = []
    for key, value in dictionnary.items():
        if len(value['script']) > 50:
            formatted_item = {
                "name": value["name"],
                "arms": value["arms"],
                "face": value["face"]
            }
            formatted_data.append(formatted_item)
    root = tk.Tk()
    root.withdraw() 
    file_path = filedialog.asksaveasfilename(
        title="Choose where to save the file animations.json",
        defaultextension=".json", 
        filetypes=[("JSON files", "*.json")],
        initialdir="../IVILSB_FRONTEND/public/FBX",
        initialfile="animations.json"  
        )
    if file_path:
        with open(file_path, 'w') as f:
            json.dump(formatted_data, f, indent=4)

# exported function
def main_client(DICTIONNARY_JSON):
    print('Fetching data...')
    data = fetch_database()
    data = clean_database(data)
    export_dictionnary_json(data, DICTIONNARY_JSON)
    export_animations_json(data)
    print(len(data), "animations fetched")
    data = remove_empty_scripts(data)
    print(len(data), "animations kept")
    return data