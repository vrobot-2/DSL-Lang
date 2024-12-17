import re
import sys
from tqdm import tqdm

def parse_api_definitions(lines):
    api_map = {}
    for line in lines:
        if line.startswith("api") or line.startswith("end"):
            continue
        cpp_func, dsl_alias = [x.strip() for x in line.split("->")]
        
        # Parse C++ function and parameters
        cpp_name = cpp_func[:cpp_func.find("(")]
        
        # Handle structured parameters
        param_str = cpp_func[cpp_func.find("(")+1:-1]
        params = []
        struct_params = []
        
        # Split parameters, handling both normal and structured params
        in_struct = False
        current_param = ""
        brace_count = 0
        
        for char in param_str:
            if char == '{':
                in_struct = True
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    in_struct = False
            elif char == ',' and not in_struct:
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ""
                continue
            current_param += char
        
        if current_param.strip():
            params.append(current_param.strip())
        
        # Parse normal and structured parameters
        cpp_params = []
        for param in params:
            if param.startswith('{'):
                # Parse structured parameters
                struct_matches = re.findall(r'\.(\w+)\s*:\s*(\w+)(?:\s*=\s*([^,}]+))?', param)
                cpp_params.extend([(name, type_, default) for name, type_, default in struct_matches])
            else:
                # Parse regular parameters
                match = re.match(r'(\w+)\s*:\s*(\w+)(?:\s*=\s*([^,)]+))?', param)
                if match:
                    cpp_params.append(match.groups())
        
        # Parse DSL command and parameters
        dsl_cmd = dsl_alias[:dsl_alias.find("(")]
        dsl_params = re.findall(r'(\w+)(?:\?)?', dsl_alias[dsl_alias.find("(")+1:-1])
        
        api_map[dsl_cmd] = {
            'cpp_name': cpp_name,
            'params': cpp_params,
            'param_map': dsl_params
        }
    return api_map

def parse_routines(lines, api_map):
    routines = {}
    current_routine = None
    commands = []
    in_block = False
    block_content = []
    current_comment = None

    for line in lines:
        line = line.strip()
        if line.startswith("//"):
            current_comment = line
            continue
        elif line.startswith("routine"):
            if current_routine:
                routines[current_routine] = {"commands": commands, "description": current_comment}
            current_routine = line.split()[1]
            commands = []
            current_comment = None
        elif line.startswith("block {"):
            in_block = True
            block_content = []
        elif line == "}" and in_block:
            in_block = False
            commands.append(("block", block_content))
        elif in_block:
            if not line.startswith("//"):  # Skip comments in blocks
                block_content.append(line)
        elif line.startswith("end"):
            if current_routine:
                routines[current_routine] = {"commands": commands, "description": current_comment}
                current_routine = None
        elif line and not line.startswith("//"):
            if current_comment:
                commands.append(("comment", current_comment))
                current_comment = None
            commands.append(line)
    return routines

def extract_initial_cpp_code(lines):
    initial_cpp_code = []
    in_initial_block = False

    for line in lines:
        if line.strip() == "initial_cpp_code":
            in_initial_block = True
            continue
        elif line.strip() == "end" and in_initial_block:
            in_initial_block = False
            break
        elif in_initial_block:
            initial_cpp_code.append(line)

    return "\n".join(initial_cpp_code)

def lint_dsl_file(filepath):
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: '{filepath}' file not found.")
        return None, None, None
    except Exception as e:
        print(f"Error reading '{filepath}': {e}")
        return None, None, None

    errors = []
    warnings = []
    api_defined = False
    routine_defined = False
    in_initial_block = False

    for i, line in enumerate(tqdm(lines, desc="Linting")):
        line = line.strip()
        
        if line.startswith("initial_cpp_code"):
            in_initial_block = True
        elif line == "end" and in_initial_block:
            in_initial_block = False
        elif in_initial_block:
            continue
        elif line.startswith("api"):
            api_defined = True
        elif line.startswith("end"):
            if api_defined:
                api_defined = False
            elif routine_defined:
                routine_defined = False
            else:
                errors.append((i + 1, "Found 'end' without a corresponding 'api' or 'routine'"))
        elif line.startswith("routine"):
            routine_defined = True
        elif line.startswith("block {"):
            if not routine_defined:
                errors.append((i + 1, "Found 'block {' outside of a routine"))
        elif line == "}" and not api_defined:
            if not routine_defined:
                errors.append((i + 1, "Found '}' outside of a routine or block"))
    
    if errors or warnings:
        print("Linting results:")
        for error in errors:
            print(f"Error at {filepath}:{error[0]}: {error[1]}")
        for warning in warnings:
            print(f"Warning at line {filepath}:{warning[0]}: {warning[1]}")
        return None, None, None

    # Extract initial C++ code
    initial_cpp_code = extract_initial_cpp_code(lines)

    api_start = lines.index("api\n")
    api_end = lines.index("end\n", api_start)

    api_lines = lines[api_start:api_end + 1]
    routine_lines = lines[api_end + 1:]

    api_map = parse_api_definitions(api_lines)
    routines = parse_routines(routine_lines, api_map)

    print(f"Linting successful for '{filepath}'")
    return api_map, routines, initial_cpp_code

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dsl_linter.py <dsl_filepath>")
    else:
        lint_dsl_file(sys.argv[1])