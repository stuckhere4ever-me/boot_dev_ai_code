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

######  IMPORTS #######
# os - for all OS level commands like file paths and enviornments
# dotenv - lets me set isolated .env files for just this project
# genai - The gemini library
# types - allows me to utilize the Content type as a message to the LLM
#######################



import os
import copy  
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

### Function - build_client ###
### This function sets up the enviornment and returns a client.
### I will eventually put a docstring in here

my_funcs = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

def build_client():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("-- API Key Not Found --")

    client = genai.Client(api_key=api_key)
    return client

### Main ###
# Program entry point #

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = copy.deepcopy(function_call_part.args)
    working_dir = "./calculator"

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

    func_to_run = my_funcs[function_name]
    function_args['working_directory'] = working_dir
    function_result = func_to_run(**function_args)


    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}") 

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

    # print(my_funcs[function_call_part.name](working_directory="calculator", **function_call_part.args))

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
    function_declarations=[schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file],
    )

    llm_config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt)
    
    response_list = []

    for _ in range (20):
    
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
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
        if args.verbose:
            print(f"User prompt: {prompt}")
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Response tokens: {response_tokens}")
    
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

        else:
            # We are done! 
            break

if __name__ == "__main__":
    main()
