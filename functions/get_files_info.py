"""
All of the relevant information with regards to the get_files_info function.
This function will the contents of a directory
"""

import os
from pathlib import Path
from google.genai import types




schema_get_files_info: types.FunctionDeclaration = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)




def get_files_info(working_directory: str, directory: str=".") -> str:
    '''
    A function to gather the contents of a directory
    Returns: String with contents of the directory or Error
    
    :param working_directory: The base directory we are working from
    :param directory: The le path of the directory we want to read
    '''

    try: 
        base = Path(working_directory).resolve()
        target = (base / directory).resolve(strict=False)

        if target != base and base not in target.parents:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not target.is_dir():
            return f'Error: "{directory}" is not a directory'

        entries = sorted(target.iterdir(), key=lambda p: p.name)
        lines = [f"- {p.name}: file_size={p.stat().st_size}, is_dir={p.is_dir()}" for p in entries]
        
        return "\n".join(lines)

    except Exception as e:
        return f"Error: {e}"
