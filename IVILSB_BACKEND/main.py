# -------------------------------------------------------
# CONSTANTS

from dotenv import load_dotenv, find_dotenv
import openai
import os

# Constants
INSTRUCTIONS = "data/instructions.txt"
DICTIONARY = "data/LSB_v5.txt"

# OpenAI API client config
ASST_ID = "asst_n6lhbk01aFIQst5Jmg2pjoAG"   # ID of the assistant. If incorrect, a new assistant will be created.
ASST_NAME = "IVI_LSB"                       # Name of the assistant
LLM_MODEL = "o1-mini-2024-09-12"            # Language model to use

# Thread config
LLM_TEMPERATURE = 0.2                       # Temperature for the language model
LLM_TOP_P = 0.9                             # Top-p parameter for the language model

# Load environment variables
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ.get("OPENAI_API_KEY")

# -------------------------------------------------------
# FUNCTIONS

from assistant import asst_init, asst_main

def prepare_text(text):
    """
    Prepare and normalize the input text by performing several transformations.

    This function :
    - Lowers the case of the text
    - Replaces accented characters
    - Removes specified punctuation
    - Replaces periods with the string "IDLE"
    - Converts the text to uppercase, and splits it into a list of words.

    Args:
        text (str): The input text to be prepared.

    Returns:
        list: A list of processed and normalized words from the input text.
    """
    res = text
    # Convert text to lowercase
    res = res.lower()
    # Replace accented characters with unaccented counterparts
    for char in "áàäâã":
        res = res.replace(char, "a")
    for char in "éèëê":
        res = res.replace(char, "e")
    for char in "íìïî":
        res = res.replace(char, "i")
    for char in "óòöôõ":
        res = res.replace(char, "o")
    for char in "úùüû":
        res = res.replace(char, "u")
    for char in "ñ":
        res = res.replace(char, "n")
    # Remove specified punctuation
    for char in "?¿,;:!¡()[]{}":
        res = res.replace(char, "")
    # Replace periods with "IDLE"
    res = res.replace(".", "IDLE")
    # Convert text to uppercase
    res = res.upper()
    # Split text into a list of words
    res = res.split(" ")
    return res

def main_process(input_text, words):
    """
    Process the input text by interpreting it using the assistant and preparing the response.

    This function initializes the assistant, sends the input text for interpretation, receives the
    response, and then prepares the text by normalizing it.

    Args:
        input_text (str): The text input to be processed and interpreted.
        words (list): A list of words relevant to the processing (usage depends on implementation).

    Returns:
        list: A list of processed and normalized words from the assistant's response.
    """
    print("text", input_text)
    print("words", words)
    
    # Initialize the assistant
    client, assistant_id, instructions, dictionary, clean_dictionary = asst_init(
        dict_path=DICTIONARY, 
        inst_path=INSTRUCTIONS, 
        asst_id=ASST_ID, 
        asst_name=ASST_NAME, 
        llm_model=LLM_MODEL)

    # Interpret the sentence using the assistant
    result = asst_main(
        client=client, 
        assistant_id=assistant_id, 
        instructions=instructions, 
        dictionary=dictionary, 
        clean_dictionary=clean_dictionary, 
        sentence=input_text,
        T=LLM_TEMPERATURE,
        P=LLM_TOP_P
    )
    
    print(result)

    # Prepare the text by normalizing it
    prepared_text = prepare_text(result)

    print(prepared_text)
    
    return prepared_text

# -------------------------------------------------------
# SERVER

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/process_text")
async def process_text(request: Request):
    """
    Endpoint to process and interpret input text.

    This endpoint receives a JSON message containing :
    - "text": The input text to be processed.
    - "words": The list of available words in the LSB dictionary.
    
    The input text is processed and interpreted using the OpenAI assistant.    

    Args:
        request (Request): The incoming HTTP request containing JSON data with keys "text" and "words".

    Returns:
        dict: A JSON response with a status indicator and the processed text.
              Example:
              {
                  "ok": True,
                  "processed_text": ["HOLA", "BUENOS_DIAS", "IDLE"]
              }
    """
    data = await request.json()
    text = data.get("text", "")
    words = data.get("words", [])
    processed_text = main_process(text, words)
    return {"ok": True, "processed_text": processed_text}

if __name__ == "__main__":
    """
    The server listens on all available IP addresses on port 8000.
    For development purposes.
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
