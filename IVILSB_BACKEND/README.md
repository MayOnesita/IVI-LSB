# IVI-LSB : Backend

This project contains the back-end code for the IVI-LSB Web Page.

### Description 

The back-end of the web page is designed to process and "translate" text written in spanish into Bolivian Spanish (written) Sign Language using OpenAI's language models.

The main steps of the process are:
- **Text Processing:** The input text is cleaned and normalized to ensure consistency. 
- **OpenAI Assistant:** The text is interpreted using the OpenAI assistant. The assistant is configured and initialized with the LSB dictionary and instructions.
- **Validation Cycle:** The interpreted text is validated against the LSB dictionary. If validation fails, the process is repeated with a new interpretation.
- **Output:** The validated text is returned as a list of available, formatted signs for the front-end.

---
### Main Functions

`main_process(input_text, words)`
- **Purpose:** Processes input text by interacting with the OpenAI assistant.
- **Functionality:** Initializes the assistant, interprets the input text, and returns a cleaned, normalized response ready for use.

`asst_init(dict_path, inst_path, asst_id, asst_name, llm_model)`
- **Purpose:** Initializes the assistant and prepares it for interaction.
- **Functionality:** Loads the LSB dictionary and assistant instructions, sets up or updates the assistant, and prepares the system for text interpretation.

`asst_main(client, assistant_id, instructions, dictionary, clean_dictionary, sentence, T, P)`
- **Purpose:** Handles the main interpretation workflow using the OpenAI assistant.
- **Functionality:** Creates a new thread for interaction, processes the sentence, and returns the interpreted output or errors if validation fails.

`process_text(request: Request)`
- **Purpose:** API endpoint to process text input.
- **Functionality:** Receives JSON data from clients, processes it using `main_process`, and returns the validated and interpreted text.

`check_sentence(dictionary, sentence)`
- **Purpose:** Validates the interpreted text against the LSB dictionary.
- **Functionality:** Checks the sentence against the dictionary and returns a list of unknown words not found in the dictionary or an error message. These words are then transferred to the OpenAI assistant for re-interpretation with additional context.

---
### Configure a new Conda environment

1- Install Miniconda (or Anaconda)
> Download **[here](https://docs.anaconda.com/miniconda/)**

2- Create the environment
`conda create --name ivilsb`

3- Activate the environment
`conda activate ivilsb`

4- Install the packages
`conda install --file requirements.txt`
