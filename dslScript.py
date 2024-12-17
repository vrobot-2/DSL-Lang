import re
import sys
from dsl_linter import lint_dsl_file, parse_api_definitions, parse_routines
from tqdm import tqdm

def translate_command(cmd_name, args, api_map):
    if cmd_name not in api_map:
        return f"// Unknown command: {cmd_name}"
    
    cmd_info = api_map[cmd_name]
    cpp_name = cmd_info['cpp_name']
    params = cmd_info['params']
    param_map = cmd_info['param_map']
    
    # Check for format string in param_map
    format_str = None
    struct_args = []
    final_args = []
    
    for i, param in enumerate(param_map):
        if param.startswith('%{') and param.endswith('}%'):
            format_str = param[2:-2]  # Remove %{ and }%
            struct_start = i
            # Extract struct arguments
            while i < len(args):
                struct_args.append(args[i])
                i += 1
            break
        elif i < len(args):
            final_args.append(args[i])
    
    if format_str:
        # Replace $1, $2, etc with actual values
        for i, arg in enumerate(struct_args, 1):
            format_str = format_str.replace(f'${i}', arg)
        final_args.append("{" + format_str + "}")
    
    return f"{cpp_name}({', '.join(final_args)})"

def compile_routines_to_cpp(routines, api_map, initial_cpp_code=""):
    cpp_code = ["// Auto-generated code from DSL\n"]
    
    if initial_cpp_code:
        cpp_code.append(initial_cpp_code)
    
    for routine_name, routine_data in routines.items():
        if routine_data["description"]:
            cpp_code.append(f"/*\n * {routine_data['description'][2:].strip()}\n */")
        cpp_code.append(f"void {routine_name}() {{")
        
        for command in routine_data["commands"]:
            if isinstance(command, tuple):
                if command[0] == "block":
                    cpp_code.append("    // Begin raw C++ block")
                    for line in command[1]:
                        cpp_code.append(f"    {line}")
                    cpp_code.append("    // End raw C++ block")
                elif command[0] == "comment":
                    cpp_code.append(f"    {command[1]}")
            else:
                parts = command.split()
                cmd_name = parts[0]
                cmd_args = parts[1:]
                translated = translate_command(cmd_name, cmd_args, api_map)
                cpp_code.append(f"    {translated};")
        
        cpp_code.append("}")
        cpp_code.append("")  # Add blank line between functions
    
    return "\n".join(cpp_code)

def update_cpp_file(new_routines, api_map, initial_cpp_code=""):
    # Generate new implementations
    new_content = compile_routines_to_cpp(new_routines, api_map, initial_cpp_code)
    
    # Write new implementations to the file
    with open("src/autonsDSL.cpp", "w") as file:
        for line in tqdm(new_content.splitlines(), desc="Writing to file"):
            file.write(line + "\n")

def main(dsl_filepath, cpp_filepath):
    print("Starting linting...")
    # Run the linter and get parsed definitions
    api_map, routines, initial_cpp_code = lint_dsl_file(dsl_filepath)

    if api_map is None or routines is None:
        print("Linting failed. Aborting compilation.")
        return

    try:
        print("Starting compilation...")
        # Generate the cpp code and write to file
        update_cpp_file(routines, api_map, initial_cpp_code)
        print(f"Successfully compiled and wrote to '{cpp_filepath}'")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python dslScript.py <dsl_filepath> <cpp_filepath>")
    else:
        main(sys.argv[1], sys.argv[2])
