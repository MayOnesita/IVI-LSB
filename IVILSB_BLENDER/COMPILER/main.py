from client import main_client
from database import main_database
from compiler import main_compiler

DATABASE_TXT = 'OUTPUT/database.txt'
DATABASE_JSON = 'OUTPUT/database.json'
DICTIONNARY_JSON = 'OUTPUT/dictionnary.json'

if __name__ == '__main__':
    # fetch and clean data from Google Sheets
    print("\n---------------------------------------------")
    print("Fetching data from Google Sheets")
    print("---------------------------------------------")
    data = main_client(DICTIONNARY_JSON)
    # create database txt file from data
    print("\n---------------------------------------------")
    print("Creating database.txt file")
    print("---------------------------------------------")
    main_database(data, DATABASE_TXT)
    # compile database.txt file into database.json file
    print("\n---------------------------------------------")
    print("Creating database.json file")
    print("---------------------------------------------")
    main_compiler(DATABASE_TXT, DATABASE_JSON)