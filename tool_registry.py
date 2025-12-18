"""
Registry for all functions used as tools by the LLM 
"""

from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file
from google.genai import types
from collections.abc import Callable
from typing import TypeAlias

ToolFn: TypeAlias = Callable[...,str]

TOOL_REGISTRY: list[tuple[types.FunctionDeclaration, ToolFn]] = [
    (schema_get_files_info, get_files_info),
    (schema_get_file_content, get_file_content),
    (schema_write_file, write_file),
    (schema_run_python_file, run_python_file),
]

def declarations() -> list[types.FunctionDeclaration]:
    '''
    Returns the schemas for any written functions
    '''
    return [schema for schema, fn in TOOL_REGISTRY]

def dispatch() -> dict[str, ToolFn]:
    '''
    Returns a dictionary containing {function_name: fn}
    '''
    return {schema.name: fn for schema, fn in TOOL_REGISTRY}