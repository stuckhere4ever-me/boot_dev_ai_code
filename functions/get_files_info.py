##################################
# Raza Ali                       #
# Boot.Dev - AI Agent Project!   #
# functions/get_file_info.py     #
##################################

# This file holds the get_file_info function.  It will get the contents of the directory with some key information and return it

####### NOTES #########
# I will eventually write an md file for this project
# All filenames, function names, variable names (except constants) are in snake_case
#######################

######  IMPORTS #######
# os - for all OS level commands like file paths and enviornments
#######################

import os
from google.genai import types




schema_get_files_info = types.FunctionDeclaration(
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


### Function - get_file_info ###
### Argument - working_directory - A string which represents the directory that I am working thorugh currently
### Argument - directory within the working directory I am looking through
### Function will return a list of everything that exists within the directory
### Note that it does not traverse down the path at all, just returns current information
### Return Value: A string representing the overall directory structure with the following structure:
### {filename}: file_size={filesize}, is_dir={True | False}
### Note that each file is on a new line


def get_files_info(working_directory, directory="."):

    # Realpath lets me manage symbolic links in the event that they show up
    # Base is the current directory I am working through 
    # Directory is the second tier I am working through

    try: 
        base = os.path.realpath(working_directory)
        target = os.path.realpath(os.path.join(base,directory))

        # Let's make sure we are allowed to work here. 
        if os.path.commonpath([base, target]) != base:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Lets make sure we are actually targeting a directory
        if not os.path.isdir(target):
            return f'Error: "{target}" is not a directory'
        
        # Sort for deterministic output
        entries = sorted(os.scandir(target), key=lambda e: e.name)
        
        # Build a list of lines with comprehension
        lines = [
            f"- {e.name}: file_size={e.stat().st_size}, is_dir={e.is_dir()}"
            for e in entries
        ]

        # Joining this way will make sure we don't have any weird trailing newlines 
        return "\n".join(lines)

    except Exception as e:
        return f"Error: {e}"
