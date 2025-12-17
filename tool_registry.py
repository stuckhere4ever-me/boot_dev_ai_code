from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

TOOL_REGISTRY = [
    (schema_get_files_info, get_files_info),
    (schema_get_file_content, get_file_content),
    (schema_write_file, write_file),
    (schema_run_python_file, run_python_file),
]

def declarations():
    return [schema for schema, fn in TOOL_REGISTRY]

def dispatch():
    return {schema.name: fn for schema, fn in TOOL_REGISTRY}