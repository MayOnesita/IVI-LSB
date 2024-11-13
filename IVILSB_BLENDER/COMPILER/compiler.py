# compiler.py
import ply.lex as lex
import ply.yacc as yacc
import json

# ----------------------------------------------------------------
# LEXER RULES

tokens = (
    'LPAREN', 
    'RPAREN', 
    'LBRACE', 
    'RBRACE', 
    'LBRACKET', 
    'RBRACKET', 
    'COMMA', 
    'DOT',
    'DASH', 
    'REPEAT', 
    'SPEED',
    'FLOAT',
    'INT',
    'STRING'
)

t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_COMMA     = r','
t_DASH      = r'-'
t_DOT       = r'\.'

def t_FLOAT(t):
    r'-?\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_REPEAT(t):
    r'REPEAT'
    print("Lexing REPEAT")
    return t

def t_SPEED(t):
    r'SPEED'
    print("Lexing SPEED")
    return t

def t_STRING(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    print(f"Lexing STRING: {t.value}")
    t.type = 'STRING'
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

t_ignore    = ' \t\n'

lexer = lex.lex()

# ----------------------------------------------------------------
# PARSER RULES

def p_program(p):
    '''program : animations'''
    print("---------------------------------------------")
    print("Compilation completed successfully")
    print("---------------------------------------------\n")
    p[0] = p[1]

def p_animations(p):
    '''animations : animation
                  | animations animation'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
    # print(f"Parsed animations: {p[0]}")

def p_animation(p):
    '''animation : LPAREN STRING RPAREN poses DOT'''
    p[0] = {p[2]: {"name": p[2], "poses": p[4]}}
    # print(f"Parsed animation: {p[0]}")
    print(f"\nCompiled: {p[2]}\n-----------------------\n")
def p_poses(p):
    '''poses : pose
             | pose COMMA poses
             | repeat
             | repeat COMMA poses
             | speed
             | speed COMMA poses'''
    if len(p) == 2:
        if isinstance(p[1], dict):
            p[0] = [p[1]]
        else:
            p[0] = p[1]
    elif len(p) == 4:
        if isinstance(p[1], dict):
            p[0] = [p[1]] + p[3]
        else:
            p[0] = p[1] + p[3]
    # print(f"Parsed poses: {p[0]}")

def p_repeat(p):
    '''repeat : REPEAT LPAREN INT COMMA poses RPAREN'''
    p[0] = p[5] * p[3]
    # print(f"Parsed repeat: {p[0]}")

def p_speed(p):
    '''speed : SPEED LPAREN INT COMMA poses RPAREN'''
    for pose in p[5]:
        pose['speed'] = p[3]
    p[0] = p[5]
    # print(f"Parsed speed: {p[0]}")

def p_pose(p):
    '''pose : LBRACE STRING COMMA vectors COMMA vectors COMMA vectors RBRACE DASH LBRACE STRING COMMA vectors COMMA vectors COMMA vectors RBRACE'''
    print(f"Hand poses: ({p[2]}, {p[12]})")
    p[0] = {
        'RH': p[2],
        'R1': p[4],
        'R2': p[6],
        'R3': p[8],
        'LH': p[12],
        'L1': p[14],
        'L2': p[16],
        'L3': p[18],
        'speed': 1  
    }
    # print(f"Parsed pose: {p[0]}")

def p_vectors(p):
    '''vectors : LBRACKET number COMMA number COMMA number RBRACKET'''
    p[0] = [p[2], p[4], p[6]]
    # print(f"Parsed vectors: {p[0]}")

def p_number(p):
    '''number : INT
              | FLOAT'''
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
        raise SyntaxError(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")
        raise SyntaxError("Unexpected end of input")

parser = yacc.yacc(write_tables=False, debug=False)

# ----------------------------------------------------------------
# MAIN EXECUTION

class SingleLineListEncoder(json.JSONEncoder):
    def encode(self, o):
        def list_to_string(lst):
            return '[' + ', '.join(map(str, lst)) + ']'
        
        def replace_lists(obj):
            if isinstance(obj, dict):
                return {k: replace_lists(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                if all(isinstance(i, (int, float)) for i in obj):
                    return list_to_string(obj)
                else:
                    return [replace_lists(i) for i in obj]
            else:
                return obj
        
        return super().encode(replace_lists(o))

def parse_input(input_string):
    try:
        lexer.input(input_string)
        result = parser.parse(input_string, lexer=lexer)
        # print(f"Parsed result: {result}")  # Added debug output
        # Use custom encoder to print lists on one line
        return json.dumps(result, indent=4, cls=SingleLineListEncoder)
    except Exception as e:
        print(f"Error during parsing: {e}")
        return None

def main_compiler(input_file, output_file):
    try:
        # Read the input file
        with open(input_file, 'r') as file:
            input_data = file.read()
        print("Input data read successfully\n")

        # Parse the input data
        parsed_json = parse_input(input_data)
        if parsed_json is not None:
            # Save the output JSON to a file
            with open(output_file, 'w') as file:
                file.write(parsed_json)
            print("---------------------------------------------")
            print(f"Data saved to {output_file} successfully")
            print("---------------------------------------------\n")
        else:
            print("Parsing failed, no output generated.")

    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")