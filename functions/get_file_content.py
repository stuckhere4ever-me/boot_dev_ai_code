from pathlib import Path
from google.genai import types

MAX_CHARS = 10000

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Lists the contents of specificed file, constrained to the working directory. Files will be Truncated at 10k characters",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path that we are going to gather contents for.",
            ),
        },
    ),
)

def get_file_content(working_directory, file_path):
    
    try:
        base = Path(working_directory).resolve()
        target = (base / file_path).resolve(strict=False)

        if target != base and base not in target.parents:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not target.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target, "r", encoding="utf-8", errors="replace") as f:
            file_content_string = f.read(MAX_CHARS + 1)
            # After reading the first MAX_CHARS...
            if len(file_content_string) > MAX_CHARS:
                file_content_string = file_content_string[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    
    except Exception as e:
        return f"Error: {e}"


    return file_content_string

