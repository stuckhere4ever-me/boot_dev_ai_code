from pathlib import Path
import subprocess
import sys

from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a python program based at file_path.  It will only work if the file ends in .py.  It can be passed a list of arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file Path of the python file to run",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Command-line arguments (each element is one arg).",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:
        base = Path(working_directory).resolve()
        target = (base / file_path).resolve(strict=False)

        if target != base and base not in target.parents:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not target.is_file():
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        command = [sys.executable, str(target)]
        if args:
            if isinstance(args,str):
                args = [args]
            command.extend(args)
    
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, cwd=str(base))
        
        return_string_lines= []

        if result.returncode != 0:
            return_string_lines.append(f'Process exited with code {result.returncode}')

        if not result.stdout and not result.stderr:
            return_string_lines.append("No Output Produced")
        
        else:
            return_string_lines.append(f'STDOUT: {result.stdout}')
            return_string_lines.append(f'STDERR: {result.stderr}')

        return "\n".join(return_string_lines)

    except Exception as e:
        return f"Error: {e}"