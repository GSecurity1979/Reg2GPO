import re
import json
import os
import argparse
from tkinter import Tk, filedialog

def parse_reg_file(reg_file_path):
    with open(reg_file_path, 'r') as file:
        content = file.read()

    # Regex patterns for different REG types
    patterns = {
        'REG_SZ': re.compile(r'\"([^\"]+)\"\s*=\s*\"([^\"]*)\"'),
        'REG_DWORD': re.compile(r'\"([^\"]+)\"\s*=\s*DWORD:\s*([0-9A-Fa-f]+)'),
        'REG_BINARY': re.compile(r'\"([^\"]+)\"\s*=\s*BINARY:\s*((?:[0-9A-Fa-f]{2}\s*)+)'),
        'REG_MULTI_SZ': re.compile(r'\"([^\"]+)\"\s*=\s*MULTI_SZ:\s*((?:\"[^\"]*\"\s*)+)'),
        'REG_QWORD': re.compile(r'\"([^\"]+)\"\s*=\s*QWORD:\s*([0-9A-Fa-f]+)')
    }
    
    reg_data = {}
    key_pattern = re.compile(r'^\[HKEY_CLASSES_ROOT\\([^]]+)\]\s*', re.MULTILINE)
    
    key_matches = key_pattern.finditer(content)
    for key_match in key_matches:
        key_path = key_match.group(1)
        key_start = key_match.end()
        next_key_match = next(key_pattern.finditer(content, key_start), None)
        key_end = next_key_match.start() if next_key_match else len(content)
        
        key_data = content[key_start:key_end]
        entries = {}
        
        for type_name, pattern in patterns.items():
            for value_match in pattern.findall(key_data):
                if type_name == 'REG_BINARY':
                    name, bin_data = value_match
                    value = bytes.fromhex(bin_data.replace(' ', ''))
                elif type_name == 'REG_MULTI_SZ':
                    name, multi_str = value_match
                    value = [s for s in multi_str.split('\r\n') if s]
                elif type_name == 'REG_QWORD':
                    name, qword = value_match
                    value = int(qword, 16)
                else:
                    name, value = value_match
                
                entries[name] = value
        
        reg_data[key_path] = entries
    
    return reg_data

def convert_to_pol(reg_data):
    # Placeholder function for conversion
    pol_data = {}
    for key_path, values in reg_data.items():
        # Example conversion logic; adjust as needed
        pol_data[key_path] = {
            "values": values
        }
    return pol_data

def save_as_json(data, output_path):
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)

def select_reg_file():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select a REG file",
        filetypes=[("Registry Files", "*.reg")]
    )
    return file_path

def main():
    reg_file = select_reg_file()
    if not reg_file:
        print("No file selected. Exiting.")
        return
    
    reg_data = parse_reg_file(reg_file)
    pol_data = convert_to_pol(reg_data)
    
    output_file = os.path.join(os.path.dirname(reg_file), 'output.pol')
    save_as_json(pol_data, output_file)
    print(f"Converted REG file '{reg_file}' to POL file '{output_file}'.")

if __name__ == "__main__":
    main()
