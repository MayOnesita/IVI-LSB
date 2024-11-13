# -------------------------------------------------------
# CONSTANTS

from dotenv import load_dotenv, find_dotenv
import openai
import os

# Constants
INSTRUCTIONS = "data/instructions.txt"
DICTIONARY = "data/LSB_v5.txt"

# OpenAI API client config
ASST_ID = "asst_n6lhbk01aFIQst5Jmg2pjoAG"
ASST_NAME = "IVI_LSB"
LLM_MODEL = "o1-mini-2024-09-12"

# Thread config
LLM_TEMPERATURE = 0.2
LLM_TOP_P = 0.9

# Load environment variables
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ.get("OPENAI_API_KEY")

# -------------------------------------------------------
# FUNCTIONS

from assistant import asst_init, asst_main

def prepare_text(text):
    res = text
    # lower the text case
    res = res.lower()
    # replace accent with no accent
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
    for char in "ç":
        res = res.replace(char, "c")
    for char in "ñ":
        res = res.replace(char, "n")
    # remove punctuation
    for char in "?¿,;:!¡()[]{}":
        res = res.replace(char, "")
    # replace . whith IDLE
    res = res.replace(".", "IDLE")
    # convert to upper case
    res = res.upper()
    # convert text to list 
    res = res.split(" ")
    return res

def main_process(input_text, words):

    print("text", input_text)
    print("words", words)
    
    # initialize
    client, assistant_id, instructions, dictionary, clean_dictionary = asst_init(
        dict_path=DICTIONARY, 
        inst_path=INSTRUCTIONS, 
        asst_id=ASST_ID, 
        asst_name=ASST_NAME, 
        llm_model=LLM_MODEL)

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

    prepared_text = prepare_text(result)

    print(prepared_text)
    
    return prepared_text

# -------------------------------------------------------
# SERVER

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_text")
async def process_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    words = data.get("words", [])
    processed_text = main_process(text, words)
    return {"ok": True, "processed_text": processed_text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
