import re 

def normalize_code(code_string):
    if not code_string:
        return ""
    code = code_string
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    # Remove all white space
    code = re.sub(r'\s+', '', code)
    return code 