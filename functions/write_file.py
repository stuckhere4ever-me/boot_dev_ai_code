from pathlib import Path
import os


from google.genai import types


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write a file, create it if it doesn't exist, or overwrite it if it does. Note this command does not append",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path that we are going to write to.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    try:
        base = Path(working_directory).resolve()
        target = (base / file_path).resolve(strict=False)

        if target != base and base not in target.parents:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if target.is_dir():
            return f'Error: Cannot write to "{file_path}" as it is a directory'
    
        os.makedirs(target.parent, exist_ok=True)

        with open(target, "w", encoding='utf-8') as f:
            f.write(content)

    except Exception as e:
        return f"Error: {e}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
