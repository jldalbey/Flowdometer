import re
import json

# Function to read the Apex class file
def read_apex_class_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to extract method signatures along with their start and end lines
def extract_method_signatures(code, methods_to_search):
    method_matches = re.finditer(r"(?P<signature>((@isTest\s+)?(public|private|protected|global)?\s+(static)?\s*(\w+)\s+(\w+)\s*\(.*\)\s*\{))", code)
    extracted_methods = []
    brackets_count = 0
    for match in method_matches:
        start_line = code[:match.start()].count('\n') + 1
        method_signature = match.group("signature").strip()
        code_subset = code[match.start():]
        lines_with_methods = {method: [] for method in methods_to_search}  # Initialize with methods to search for

        for i, char in enumerate(code_subset):
            if char == '{':
                brackets_count += 1
            elif char == '}':
                brackets_count -= 1
                if brackets_count == 0:
                    end_line = start_line + code_subset[:i].count('\n')
                    method_code = code_subset[:i]
                    for line_num, line in enumerate(method_code.split('\n'), start=start_line):
                        for method in methods_to_search:
                            if f"{method}(" in line:  # Ensuring we're looking at a method call
                                lines_with_methods[method].append(line_num)
                    
                    # Include only methods that call other specified methods
                    called_methods = {k: v for k, v in lines_with_methods.items() if v}
                    if called_methods:
                        extracted_methods.append({
                            "start": start_line,
                            "signature": method_signature,
                            "called_methods": called_methods,
                            "end": end_line
                        })
                    break

    return extracted_methods

# List of methods to search for within each method body
methods_to_search = ['preparingResponse', 'parseRecordsToFlow', 'getQueryModifiers', 'getLatestHistoryValues', 'getStringNotNull', 'isCustomObject']

# List of Apex test class paths
apex_test_class_paths = [
    "F:\\Muse Operations Drive\\Projects\\Flowdometer\\force-app\\main\\default\\classes\\ListenerFlowControllerTest1.cls",
    "F:\\Muse Operations Drive\\Projects\\Flowdometer\\force-app\\main\\default\\classes\\ListenerFlowControllerTest2.cls"
]

final_output = {}

# Loop over each file path
for path in apex_test_class_paths:
    # Read the Apex class file content
    apex_test_class_code = read_apex_class_file(path)

    # Extract method signatures and their corresponding lines
    extracted_methods_info = extract_method_signatures(apex_test_class_code, methods_to_search)

    # Add to final output
    final_output[path] = extracted_methods_info

# Prettify the output using JSON formatting
json_output = json.dumps(final_output, indent=4)
print(json_output)