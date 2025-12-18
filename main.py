"""
CLI Entry point for Gemini based coding agent
Reads GEMINI_API_KEY, runs tool loop, returns final response
"""

import os
import copy  
import argparse
import config
import tool_registry

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt

my_funcs = tool_registry.dispatch()

def build_client():
    '''
    requires env variable GEMINI_API_KEY
    Returns a client that can make Gemini calls
    Raises: Runtime Error if API Key not found
    '''

    load_dotenv()
    api_key = os.environ.get(config.API_KEY_LOCATION)
    if api_key is None:
        raise RuntimeError("-- API Key Not Found --")

    client = genai.Client(api_key=api_key)
    return client



def call_function(function_call_part, verbose=False):
    '''
    Function that takes an instruction from LLM and will execute it
    Constraint: We do not trust the model to detemrine working directory, so we inject it.
    
    :param function_call_part: Parts of the funciton call returned from Gemini
    :param verbose: Boolean - Determines if extra output is needed
    '''
    function_name = function_call_part.name
    function_args = copy.deepcopy(function_call_part.args)


    # This will return a response that basically says LLM gave me something it was not supoposed to
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

    # Inject sandboxed working directory before executing tool
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


def main():
    '''
    Run will send the user prompt to Gemini and complete actions based on LLM response
    Constraint: LLM will run no more than config.MAX_ITERATIONS times.
    CLI takes two arguments: user_prompt: Required.  What we want the LLM to do.
    verbose: If set will put extra output to the console
    '''

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

    for _ in range (config.MAX_ITERATIONS):

        # Messages are never reset, they include full history every time so that LLM can see all prior information
        response_list = []
        response = client.models.generate_content(
            model=config.MODEL, 
            contents=messages,
            config=llm_config,
        )

        metadata = response.usage_metadata
    
        if metadata is None:
            raise RuntimeError ("--Failed API Call --")

        # Append candidates prior to function calls in case there are multiple reponses that may come back         
        for candidate in response.candidates:
            messages.append(candidate.content)


        prompt_tokens = metadata.prompt_token_count
        response_tokens = metadata.candidates_token_count

        if args.verbose:
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
            break

        else:
            break

if __name__ == "__main__":
    main()
