##################################
# Raza Ali                       #
# Boot.Dev - AI Agent Project!   #
# main.py                        #
##################################

# This file acts as the entry point to the overall program.  It is educationary in nature, so there will be some weird things
# in each revision that I will likely change out.  I am in the process of learning python and relearning development so lets
# see how badly I can mess things up.

### Project Description - Write a primitive AI Coding agent which utilizes gemini's flash model to re-write bad code
### Key Learning Concepts - os / sys commands, functional programming, a little bit of LLM, documentation

####### NOTES #########
# I will eventually write an md file for this project
# All filenames, function names, variable names (except constants) are in snake_case
#######################

###### IMPORTS #######
# All of these are external modules
# os - for all OS level commands like file paths and enviornments
# copy - for dictionary deepcopy
# argparse - lets me take command line arguments
# dotenv - lets me set isolated .env files for just this project
# genai - The gemini library
# types - allows me to utilize the Content type as a message to the LLM
#
#######################

import os
import copy  
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

###### IMPORTS #######
# All of these are custom built modules
# prompts - contains my system prompt
# get_files_info - contains the functions that will list directory information
# get_file_content - contains the functions that get file content
# run_python_files - contains the functions run python files
# write_files - contains the functions that write files to the filesystem
#######################

from prompts import system_prompt
# from functions.get_files_info import schema_get_files_info, get_files_info
# from functions.get_file_content import schema_get_file_content, get_file_content
# from functions.run_python_file import schema_run_python_file, run_python_file
# from functions.write_file import schema_write_file, write_file
import config
import tool_registry

### Dictionary - my_funcs
### These are the functions that are available to us to send to Gemini

# my_funcs = {
#     "get_files_info": get_files_info,
#     "get_file_content": get_file_content,
#     "run_python_file": run_python_file,
#     "write_file": write_file,
# }

my_funcs = tool_registry.dispatch()

### Function - build_client ###
### This function sets up the enviornment and returns a client.

def build_client():
    load_dotenv()
    api_key = os.environ.get(config.API_KEY_LOCATION)
    if api_key is None:
        raise RuntimeError("-- API Key Not Found --")

    client = genai.Client(api_key=api_key)
    return client


### Function - call_function ###
### This function will act as a worker and take the information that is provided by the gemini response and use it to call the requested functions

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = copy.deepcopy(function_call_part.args)


    # This will return a response that basically says you gave me something you weren't supposed to
    if function_name not in my_funcs:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                name=function_name,
                response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # func_to_run is a function based on what is returned by the LLM.  We need to give it a working directory.  I used the deepcopy just in case function_call_part.args had weird behavior
    func_to_run = my_funcs[function_name]
    function_args['working_directory'] = config.WORKING_DIR
    function_result = func_to_run(**function_args)


    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}") 

    # Return the response in a way I can give it back to the LLM 
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


### Main ###
# Program entry point #
def main():
    
    # Gather all the arguments - This needs to turn into its own function later.
    # I also really dislike how much I have to hard code stuff
    # Potential function will build out a dictionary with a bunch of information (description, initial prompt, is_verbose, etc)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User Prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    prompt = args.user_prompt

    client = build_client()
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    available_functions = types.Tool(
    function_declarations=tool_registry.declarations(),
    )

    llm_config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt)
    
    if args.verbose:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")

    for _ in range (config.MAX_ITERATIONS):
    
        response_list = []
        response = client.models.generate_content(
            model=config.MODEL, 
            contents=messages,
            config=llm_config,
        )

        metadata = response.usage_metadata
    
        if metadata is None:
            raise RuntimeError ("--Failed API Call --")

        for candidate in response.candidates:
            messages.append(candidate.content)

        prompt_tokens = metadata.prompt_token_count
        response_tokens = metadata.candidates_token_count

        # I am certain I can use a decorator to add a logger of sorts that will only log if verbose is set.
        # Maybe I can build out a log that drops into a json file when i'm done, similar to what they did for asteroids

    
        if response.function_calls:
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose=args.verbose)

                if not function_call_result.parts[0].function_response.response:
                    raise Exception ("ERROR: FATAL EXCEPTION - Something went wrong")
                
                response_list.append(function_call_result.parts[0])
                
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
            
            messages.append(types.Content(role="user", parts=response_list))

        elif response.text:
            print (response.text)
            break

        else:
            break

if __name__ == "__main__":
    main()
