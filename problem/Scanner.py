import json
import sys
def generate_c_file(out_f, p_Data, user_code, input_data):
    header_files = p_Data["header_files"]
    int_main = p_Data["int_main"]
    required_function = p_Data["required_function"]
    program = header_files + "\n" + user_code + "\n" + int_main + "\n"
    for line in input_data.splitlines():
        inputs = line.strip()
        program += f"    printf(\"%d\\n\", {required_function}{inputs}));\n"
    program += "    return 0;\n}"
    with open(out_f, "w") as f:
        f.write(program)
if __name__ == "__main__":
    out_f, p_Data_json, user_code, input_data = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    p_Data = json.loads(p_Data_json)
    try:
        generate_c_file(out_f, p_Data, user_code, input_data)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)