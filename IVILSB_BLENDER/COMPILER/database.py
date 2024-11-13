# database.py

def clean_database(data):
    # print("database size:", len(data), len(data[0]))
    # find indexes of columns
    i_word = data[0].index('Words')
    i_face = data[0].index('Face')
    i_script = data[0].index('Script')
    # create list of words
    word_list = []  
    for i in range(1, len(data)):
        word_list.append(data[i][i_word])
    word_list.sort()
    # create dictionary
    dictionnary = {}
    count = 0
    for row in data[1:]:
        dictionnary[count] = {
            'name': row[i_word],
            'face': row[i_face],
            'script': row[i_script]
        }
        count += 1
    # add "arms" key to each entry
    # animation is same as name, but only lowercase alphabet is allowed and spaces are replaced with underscores
    for k, v in dictionnary.items():
        name = v['name']
        arms = format_name(name)
        dictionnary[k]['arms'] = arms
    return dictionnary

def format_name(name):
    res = name.lower()
    # replace spaces with underscores
    res = res.replace(' ', '_')
    # replace characters
    for c in res:
        # replace special characters
        if c in '!¡?¿.,;:*+-=|@#$%&/\\^~`{}"\'':
            res = res.replace(c, '')
        # replace accented characters
        if c in 'áàâä':
            res = res.replace(c, 'a')
        elif c in 'éèêë':
            res = res.replace(c, 'e')
        elif c in 'íìîï':
            res = res.replace(c, 'i')
        elif c in 'óòôö':
            res = res.replace(c, 'o')
        elif c in 'úùûü':
            res = res.replace(c, 'u')
        elif c in 'ñ':
            res = res.replace(c, 'n')
    # switch to upper
    res = res.upper()
    return res

def remove_empty_scripts(dictionnary):
    dictionary_copy = dictionnary.copy()
    for k, v in dictionnary.items():
        if len(v['script']) < 55:
            del dictionary_copy[k]
    return dictionary_copy

import re

def auto_indentate(script):
    # Remove all spaces, line breaks, and tabulations
    script = re.sub(r'\s+', '', script)
    
    indent_level = 0
    indent_step = "    "
    formatted_lines = []

    # Regular expression patterns for different cases
    speed_repeat_pattern = re.compile(r'^(SPEED|REPEAT)\(\d+,')
    pose_pattern = re.compile(r'\{[A-Za-z_0-9]+,\[(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\],\[(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\],\[(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\]\}-\{[A-Za-z_0-9]+,\[(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\],\[(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\],\[(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\]\}')
     
    index = 0
    while index < len(script):
        if script[index:index+6] == 'SPEED(' or script[index:index+7] == 'REPEAT(':
            match = speed_repeat_pattern.match(script[index:])
            if match:
                formatted_lines.append(indent_step * indent_level + match.group(0))
                indent_level += 1
                index += len(match.group(0))
        elif script[index] == ')':
            indent_level -= 1
            formatted_lines.append(indent_step * indent_level + ')')
            index += 1
            # Ensure the comma is preserved if it exists after closing parenthesis
            if index < len(script) and script[index] == ',':
                formatted_lines[-1] += ','
                index += 1
        else:
            match = pose_pattern.match(script[index:])
            if match:
                formatted_lines.append(indent_step * indent_level + match.group(0))
                index += len(match.group(0))
                # Ensure the comma is preserved if it exists
                if index < len(script) and script[index] == ',':
                    formatted_lines[-1] += ','
                    index += 1
                if match.group(0).endswith('.'):
                    formatted_lines.append("")
                elif match.group(0).endswith(','):
                    formatted_lines.append(indent_step * indent_level)
            else:
                index += 1

    formatted_script = '\n'.join(formatted_lines).strip()
    if not formatted_script.endswith('.'):
        formatted_script += '.'
    return formatted_script


def main_database(data, output_file):
    with open(output_file, "w") as file:
        file.write("(IDLE)\n\n")
        file.write("SPEED(2,\n")
        file.write("    {R_P3, [0.28, -0.11, 0.94], [0.00, 0.27, 0.00], [0.22, 0.33, 0.00]} - ")
        file.write("{L_P3, [0.28, -0.11, 0.94], [0.00, 0.27, 0.00], [0.22, 0.33, 0.00]},\n")
        file.write("    {R_P3, [0.29, -0.10, 0.95], [0.01, 0.28, 0.01], [0.23, 0.34, 0.01]} - ")
        file.write("{L_P3, [0.29, -0.10, 0.95], [0.01, 0.28, 0.01], [0.23, 0.34, 0.01]}\n")
        file.write(").\n\n")
        for key, value in data.items():
            file.write(f"({value['arms']})\n\n")
            formatted_script = auto_indentate(value['script'])
            # formatted_script = value['script']
            file.write(f"{formatted_script}\n\n")
    print("Database file created successfully")