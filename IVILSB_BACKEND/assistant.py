import openai
import time
import difflib

# ----------------------------------------------------------------
# FUNCTIONS

def load_file(filepath):
    """
    Load the contents of a file.
    Returns the contents as a string.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        glossary_data = file.read()
    return glossary_data

def clean_text(text):
    """
    Clean the input text by converting it to lowercase and removing punctuation.
    Returns the cleaned text.
    """
    res = text
    # Convert text to lowercase
    res = res.lower()
    # Remove specified punctuation characters
    for char in ",;:!¡()[]{}":
        res = res.replace(char, "")
    return res

def check_sentence(dictionary, sentence):
    """
    Check a sentence for words that are not present in the provided dictionary.

    Args:
        dictionary (list): A list of valid words.
        sentence (list): A list of words from the sentence to be checked.

    Returns:
        list: A list of unknown words not found in the dictionary.
    """
    unknown_words = []
    for word in sentence:
        # Accept single-letter alphabetic words
        if len(word) == 1 and word.isalpha():
            continue
        # Accept single-number words
        if len(word) == 1 and word.isnumeric():
            continue
        # Accept punctuation points
        if word == ".":
            continue
        # Add word to unknown_words if not in dictionary
        if word not in dictionary:
            unknown_words.append(word)
    return unknown_words

def find_similar_word(dictionary, word):
    """
    Find words in the dictionary that are similar to the given word.

    Args:
        dictionary (list): A list of valid words.
        word (str): The word to find similar matches for.

    Returns:
        list or None: A list of similar words if found, otherwise None.
    """
    word = word.lower().replace(" ", "_")
    similar_words = difflib.get_close_matches(word, dictionary, n=3, cutoff=0.7)
    if similar_words:
        return similar_words
    else:
        return None 

def interpret(client, thread_id, assistant_id, instructions, dictionary, clean_dictionary, sentence, temperature, top_p):
    """
    Interpret a sentence using the assistant, ensuring all words comply with the provided dictionary.
    
    Execution:
        - Send the sentence to the assistant.
        - Check the response for unknown words.
        - If there are unknown words, find similar words in the dictionary and complete the prompt with them.
        - Retry the interpretation with the updated prompt. 
        - Repeat until the response is correct or the maximum number of attempts is reached.

    Args:
        client (openai.OpenAI): The OpenAI API client instance.
        thread_id (str): The ID of the conversation thread.
        assistant_id (str): The ID of the assistant to use.
        instructions (str): Instructions for the assistant.
        dictionary (list): A list of valid words.
        clean_dictionary (list): A cleaned list of valid words (lowercase, no punctuation).
        sentence (str): The sentence to interpret.
        temperature (float): Sampling temperature for the assistant's response.
        top_p (float): Nucleus sampling parameter for the assistant's response.

    Returns:
        str or None: The assistant's interpreted response if successful, otherwise None.
    """
    correct = False  # Flag to check if the response complies with LSB
    intento = 1      # Number of attempts
    response = None  # Response from GPT

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
            # Convert response to lists of words
            original_response = response.split()
            clean_response = (clean_text(response)).split()
            # Identify unknown words
            unknown_words = check_sentence(clean_dictionary, clean_response)
            if len(unknown_words) == 0:
                correct = True
            else:
                # Prepare additional prompt sentences for unknown words
                sentences = []
                unknown_words = list(set(unknown_words))  # Remove duplicates
                for clean_word in unknown_words:
                    # Retrieve the original unclean word
                    original_word = unclean_word(
                        dictionary=original_response, 
                        clean_dictionary=clean_response, 
                        clean_word=clean_word)
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
    # Return None if unable to interpret correctly after retries
    if not correct:
        print("No se pudo interpretar la respuesta.")
        return None
    else:
        return response

def unclean_word(dictionary, clean_dictionary, clean_word):
    """
    Retrieve the original word corresponding to a cleaned word from the dictionary.

    Args:
        dictionary (list): The original list of words.
        clean_dictionary (list): The cleaned list of words.
        clean_word (str): The cleaned word to find the original for. By cleaned, we mean lowercase and no punctuation.

    Returns:
        str or None: The original word if found, otherwise None.
    """
    try:
        index = clean_dictionary.index(clean_word)
        return dictionary[index]
    except ValueError:
        print("ERROR: word not found in dictionary")
        return None

# ----------------------------------------------------------------
# GPT FUNCTIONS

def createOrUpdateAssistant(asst_id, asst_name, llm_model, client, instructions):
    """
    Create a new assistant or update an existing one with the provided parameters.

    Args:
        asst_id (str): The ID of the assistant to update. If None, a new assistant is created.
        asst_name (str): The name of the assistant.
        llm_model (str): The language model to use for the assistant.
        client (openai.OpenAI): The OpenAI API client instance.
        instructions (str): Instructions or prompts for the assistant.

    Returns:
        str: The ID of the created or updated assistant.
    """
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

def createThread(client):
    """
    Create a new conversation thread.

    Args:
        client (openai.OpenAI): The OpenAI API client instance.

    Returns:
        str or None: The ID of the created thread, or None if creation failed.
    """
    try:
        thread = client.beta.threads.create()
        print(f"New thread created with ID: {thread.id}")
        return thread.id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

def chatWithGPT(client, thread_id, assistant_id, instructions, user_prompt, temperature, top_p):
    """
    Send a user prompt to the assistant and retrieve the response.

    Args:
        client (openai.OpenAI): The OpenAI API client instance.
        thread_id (str): The ID of the conversation thread.
        assistant_id (str): The ID of the assistant to interact with.
        instructions (str): Instructions for the assistant.
        user_prompt (str): The user's prompt to send.
        temperature (float): Sampling temperature for the assistant's response.
        top_p (float): Nucleus sampling parameter for the assistant's response.

    Returns:
        str or None: The assistant's response if successful, otherwise None.
    """
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
        return None

def waitForRunCompletion(client, thread_id, run_id, sleep_interval=5, max_retries=15):
    """
    Wait for a run to complete and retrieve the response.

    Args:
        client (openai.OpenAI): The OpenAI API client instance.
        thread_id (str): The ID of the conversation thread.
        run_id (str): The ID of the run to wait for.
        sleep_interval (int, optional): Seconds to wait between retries. Defaults to 5.
        max_retries (int, optional): Maximum number of retries. Defaults to 15.

    Returns:
        str or None: The assistant's response if the run completes successfully, otherwise None.
    """
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
                if messages.data:
                    last_message = messages.data[-1]
                    response = last_message.content
                    return response
                else:
                    print("No messages found in the thread.")
                    return None

        except Exception as e:
            print(f"Error while retrieving the run: {e}")
            retries += 1
            print(f"Retry {retries}/{max_retries}")

        print(f"Waiting for run to complete... (Attempt {retries + 1}/{max_retries})")
        time.sleep(sleep_interval)
    
    print("Max retries reached. Exiting wait loop.")
    return None

# ----------------------------------------------------------------
# MAIN EXECUTION

def asst_init(dict_path, inst_path, asst_id, asst_name, llm_model):
    """
    Initialize the assistant by loading necessary data and setting up the assistant.

    Args:
        dict_path (str): Path to the LSB dictionary file.
        inst_path (str): Path to the assistant instructions file.
        asst_id (str): The ID of the assistant to update or None to create a new one.
        asst_name (str): The name of the assistant.
        llm_model (str): The language model to use for the assistant.

    Returns:
        tuple: A tuple containing the OpenAI client, assistant ID, instructions, dictionary list, and cleaned dictionary list.
    """
    print("\n-------------------------------")
    print("INITIATION\n")
    client = openai.OpenAI()

    # Load glossary data and instructions
    glossary_data = load_file(dict_path)
    instructions = load_file(inst_path)

    # Replace line breaks with space and convert to lists
    glossary_data = glossary_data.replace("\n", " ")
    dictionary = glossary_data.split()
    dictionary.sort()
    clean_dictionary = (clean_text(glossary_data)).split()
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
    """
    Main function to interpret a sentence using the assistant.

    Args:
        client (openai.OpenAI): The OpenAI API client instance.
        assistant_id (str): The ID of the assistant to use.
        instructions (str): Instructions for the assistant.
        dictionary (list): A list of valid words.
        clean_dictionary (list): A cleaned list of valid words.
        sentence (str): The sentence to interpret.
        T (float): Sampling temperature for the assistant's response.
        P (float): Nucleus sampling parameter for the assistant's response.

    Returns:
        str or None: The interpreted sentence from the assistant if successful, otherwise None.
    """
    # Create a new thread
    thread_id = createThread(client)

    print("\n-------------------------------")
    print("INTERPRETATION")

    # Interpret the sentence
    result = interpret(
        client=client, 
        thread_id=thread_id, 
        assistant_id=assistant_id, 
        instructions=instructions, 
        dictionary=dictionary, 
        clean_dictionary=clean_dictionary, 
        sentence=sentence,
        temperature=T,
        top_p=P
        )
    
    print("\n-------------------------------\n")
    
    return result

if __name__ == "__main__":
    """
    Entry point of the script. Initializes the assistant and processes a sample sentence multiple times,
    writing the results to a specified file.
    """

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
    
    sentence = "Hola, soy IVILSB!"
    
    # Initialize the assistant
    client, assistant_id, instructions, dictionary, clean_dictionary = asst_init(
        dict_path=DICTIONARY, 
        inst_path=INSTRUCTIONS, 
        asst_id=ASST_ID, 
        asst_name=ASST_NAME, 
        llm_model=LLM_MODEL)

    with open(RESULTS, "w", encoding="utf-8") as file:
        for k in range(3):
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
