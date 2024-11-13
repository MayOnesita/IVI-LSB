import openai
import time
import difflib

# ----------------------------------------------------------------
# FUNCTIONS

def load_file(file):
    with open(file, 'r', encoding='utf-8') as file:
        glossary_data = file.read()
    return glossary_data

def text_to_list(text):
    return text.split()

def clean_text(text):
    res = text
    # lower the text 
    res = res.lower()
    # remove punctuation
    for char in ",;:!¡()[]{}":
        res = res.replace(char, "")
    return res

def check_sentence(dictionary, sentence):
    unknown_words = []
    for word in sentence:
        # if the word is a single letter, accept it
        if len(word) == 1 and word.isalpha():
            continue
        # if the word is a single number, accept it
        if len(word) == 1 and word.isnumeric():
            continue
        # if the word is a point, accept it
        if word == ".":
            continue
        # if the word is not in the dictionary, add it to the list
        if word not in dictionary:
            unknown_words.append(word)
    return unknown_words

def find_similar_word(dictionary, word):
    word = word.lower().replace(" ", "_")
    similar_words = difflib.get_close_matches(word, dictionary, n=3, cutoff=0.7)
    if similar_words:
        return similar_words
    else:
        return None 

def interpret(client, thread_id, assistant_id, instructions, dictionary, clean_dictionary, sentence, temperature, top_p):
    """_summary_

    Args:
        client (_type_): _description_
        thread_id (_type_): _description_
        assistant_id (_type_): _description_
        instructions (_type_): _description_
        dictionary (_type_): _description_
        clean_dictionary (_type_): _description_
        sentence (_type_): _description_
        temperature (_type_): _description_
        top_p (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    correct = False # Check if the response is compliant with LSB
    intento = 1 # Number of attempts
    response = None # Response from GPT

    init_prompt = "INTERPRETA AL LSB: " + sentence
    full_prompt = (
        init_prompt +
        "\n\n Dictionario LSB: " + 
        ", ".join(dictionary)
    )

    while (not correct) and (intento < 6):
        print("\n _____________ ")
        print("|             |")
        print("| intento: ", intento, "|")
        print("|_____________|\n")
        intento += 1
        #print("Prompt: \n\n", full_prompt)

        # Send the prompt to the assistant
        response = chatWithGPT(
            client=client, 
            thread_id=thread_id, 
            assistant_id=assistant_id, 
            instructions=instructions, 
            user_prompt=full_prompt, 
            temperature=temperature, 
            top_p=top_p)
        if response:
            print("Response :", response)
            # Change the format of the response to a list of words
            original_response = text_to_list(response)
            clean_response = text_to_list(clean_text(response))
            #print("Original response: ", original_response)
            #print("Clean response:    ", clean_response)            
            # Get the list of (cleaned) words which are not in LSB
            unknown_words = check_sentence(clean_dictionary, clean_response)
            if len(unknown_words) == 0:
                correct = True
            else:
                # Additional prompt sentences
                sentences = []
                # Remove duplicates
                unknown_words = list(set(unknown_words))
                # For each unknown word, find similar words in the dictionary
                for clean_word in unknown_words:
                    # Begin the sentence with the unknown word
                    original_word = unclean_word(
                        dictionary=original_response, 
                        clean_dictionary=clean_response, 
                        clean_word=clean_word)
                    #print("Clean unknown word:    ", clean_word)
                    #print("Original unknown word: ", original_word)
                    sentence = "- " + original_word
                    # Find similar words in the dictionary
                    found_words = find_similar_word(dictionary, original_word)
                    if found_words:
                        found_words = [clean_text(word) for word in found_words]
                        sentence += " | Palabras similares: " + ", ".join(found_words)
                        print(sentence)
                    else:
                        sentence += " | No hay palabra similar en el LSB."
                        print(sentence)
                    sentences.append(sentence)
                full_prompt = (
                    init_prompt +
                    "\n\nEstas palabras NO ESTAN EN EL LSB. Por favor cambia estas palabras: " +
                    "\n".join(sentences) +
                    "\nSi no hay palabras similares adecuadas, utiliza otra palabra o reformula toda la frase." +
                    "\nIMPORTANTE: las palabras similares solo son recomendaciones automaticas, es posible que esas palabras no sean adecuadas."
                )    
        else:
            print("No response from GPT.")
            break
    # At the end of the loop, if the response is not correct, return None
    if not correct:
        print("No se pudo interpretar la respuesta.")
        return None
    # If the response is correct, return the GPT response
    else:
        return response
    
def unclean_word(dictionary, clean_dictionary, clean_word):
    try:
        index = clean_dictionary.index(clean_word)
        return dictionary[index]
    except:
        print("ERROR: word not found in dictionary")
        return None

# ----------------------------------------------------------------
# GPT FUNCTIONS

# Function to create or update the assistant
def createOrUpdateAssistant(asst_id, asst_name, llm_model, client, instructions):
    try:
        assistant = client.beta.assistants.update(
            assistant_id=asst_id,
            name=asst_name,
            model=llm_model,
            instructions=instructions,
        )
        print(f"Assistant updated with ID: {asst_id}")
        return asst_id
    except Exception as e:
        print(f"Error updating assistant: {e}")
        assistant = client.beta.assistants.create(
            name=asst_name,
            model=llm_model,
            instructions=instructions,
        )
        print(f"New assistant created with ID: {assistant.id}")
        return assistant.id

# Function to create a new thread
def createThread(client):
    try:
        thread = client.beta.threads.create()
        print(f"New thread created with ID: {thread.id}")
        return thread.id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

# Function to send a prompt to the assistant
def chatWithGPT(client, thread_id, assistant_id, instructions, user_prompt, temperature, top_p):
    try:
        print(f"Sending user prompt...")
        message = client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_prompt
        )
        print("Creating run...")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=instructions,
            temperature=temperature, 
            top_p=top_p 
        )
        print(f"Run created with ID: {run.id}, waiting for completion...")
        return waitForRunCompletion(
            client=client, 
            thread_id=thread_id, 
            run_id=run.id)
    except Exception as e:
        print(f"Error during chat: {e}")

# Function to wait for the run to complete
def waitForRunCompletion(client, thread_id, run_id, sleep_interval=5, max_retries=15):
    retries = 0

    while retries < max_retries:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            print(f"Run status: {run.status}")

            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response

        except Exception as e:
            print(f"Error while retrieving the run: {e}")
            retries += 1
            print(f"Retry {retries}/{max_retries}")

        print(f"Waiting for run to complete... (Attempt {retries + 1}/{max_retries})")
        time.sleep(sleep_interval)
        retries += 1
    
    print("Max retries reached. Exiting wait loop.")
    return None


# ----------------------------------------------------------------
# MAIN EXECUTION

def asst_init(
        dict_path, 
        inst_path, 
        asst_id, 
        asst_name, 
        llm_model):
    
    print("\n-------------------------------")
    print("INITATION\n")
    client = openai.OpenAI()

    # Load glossary data and instructions
    glossary_data = load_file(dict_path)
    instructions = load_file(inst_path)

    # Replace line breaks with comma
    glossary_data = glossary_data.replace("\n", " ")
    dictionary = text_to_list(glossary_data)
    dictionary.sort()
    clean_dictionary = text_to_list(clean_text(glossary_data))
    clean_dictionary.sort()
    print("Dictionary loaded with", len(clean_dictionary), "words")

    # Create or update the assistant with instructions
    assistant_id = createOrUpdateAssistant(
        asst_id=asst_id,
        asst_name=asst_name,
        llm_model=llm_model,
        client=client, 
        instructions=instructions)
    
    print("\n-------------------------------\n")
    return (client, assistant_id, instructions, dictionary, clean_dictionary)

def asst_main(client, assistant_id, instructions, dictionary, clean_dictionary, sentence, T, P):

    # Create a new thread
    thread_id = createThread(client)

    print("\n-------------------------------")
    print("INTERPRETATION")
    #print("Sentence: ", sentence)
    #print("Dictionary: ", dictionary)
    #print("Clean dictionary: ", clean_dictionary)

    # interpret the sentence
    result = interpret(
        client=client, 
        thread_id=thread_id, 
        assistant_id=assistant_id, 
        instructions=instructions, 
        dictionary=dictionary, 
        clean_dictionary=clean_dictionary, 
        sentence=sentence,
        temperature = T,
        top_p = P
        )
    
    print("\n-------------------------------\n")
    
    return result

if __name__ == "__main__":

    # Constants
    INSTRUCTIONS = "data/instructions.txt"
    DICTIONARY = "data/LSB_v5.txt"
    RESULTS = "results/results.txt"

    # OpenAI API client config
    ASST_ID = "asst_n6lhbk01aFIQst5Jmg2pjoAG"
    ASST_NAME = "IVI_LSB"
    LLM_MODEL = "gpt-4o-2024-08-06"

    # Thread config
    LLM_TEMPERATURE = 0.2
    LLM_TOP_P = 0.9
    
    # t_init = 0.1
    # p_init = 0.7
    sentence = "Hola, soy IVILSB!"
    
    # initialize
    client, assistant_id, instructions, dictionary, clean_dictionary = asst_init(
        dict_path=DICTIONARY, 
        inst_path=INSTRUCTIONS, 
        asst_id=ASST_ID, 
        asst_name=ASST_NAME, 
        llm_model=LLM_MODEL)

    with open(RESULTS, "w", encoding="utf-8") as file:
        # for i in range(3):
        #     for j in range(3):
        #         t = round(t_init + 0.1*i, 1)
        #         p = round(p_init + 0.1*j, 1)
        #         file.write(f"T: {t}\n")
        #         file.write(f"P: {p}\n\n")
        for k in range(3):
            #print(f"t: {t}, p: {p}, k: {k}")
            result = asst_main(
                client=client, 
                assistant_id=assistant_id, 
                instructions=instructions, 
                dictionary=dictionary, 
                clean_dictionary=clean_dictionary, 
                sentence=sentence,
                T=LLM_TEMPERATURE,
                P=LLM_TOP_P
                )
            if result:
                file.write(result + "\n")
            else:
                file.write("ERROR.\n")
        file.write("\n")