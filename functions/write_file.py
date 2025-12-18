"""
All of the relevant information with regards to the write_file function.
This function will write content of a file to a directory
"""
from pathlib import Path
from google.genai import types


schema_write_file: types.FunctionDeclaration = types.FunctionDeclaration(
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
        required=["file_path", "content"],
    ),
)

def write_file(working_directory: str, file_path, content: str) -> str:
    '''
    Docstring for write_file
    A function to write content to a file in working directory named file_path
    Returns: Successfully wrote to {file_path} ({num_characters} characters written)
    :param working_directory: The base of our working area
    :param file_path: The relative path of the file we want to write
    :param content: The content we want to write to the file

    '''
    try:
        base = Path(working_directory).resolve()
        target = (base / file_path).resolve(strict=False)

        if target != base and base not in target.parents:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if target.is_dir():
            return f'Error: Cannot write to "{file_path}" as it is a directory'
    
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, "w", encoding='utf-8') as f:
            f.write(content)

    except Exception as e:
        return f"Error: {e}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
