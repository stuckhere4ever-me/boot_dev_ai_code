# boot_dev_ai_code

A small CLI-based coding agent built as part of the Boot.dev AI Agent project. It uses Gemini (via `google-genai`) plus a small set of sandboxed “tools” to inspect and modify a local working directory.

This repo is intentionally simple and educational.

## What it does

The agent accepts a single prompt on the command line, sends it to Gemini, and (optionally) executes tool calls requested by the model until it produces a final text response or hits a max-iteration limit.

Available tools:

- `get_files_info`: list files in a directory (names, sizes, is_dir)
- `get_file_content`: read a file (truncated to a max character limit)
- `write_file`: create/overwrite a file (creates parent directories as needed)
- `run_python_file`: execute a `.py` file with optional args

All tool access is constrained to a configured working directory. The LLM never supplies the working directory directly; it is injected by the program.

## Repo layout

- `main.py`  
  CLI entrypoint and agent loop.
- `prompts.py`  
  System prompt used for the agent.
- `config.py`  
  Central config values (model, working dir, limits).
- `tool_registry.py`  
  Single source of truth for tool schemas + dispatch mapping.
- `functions/`  
  Tool implementations and their Gemini schemas.
- `calculator/`  
  Sample project used as the sandbox working directory and for tests.
- `test_*.py`  
  Simple local tests for the tool functions.

## Requirements

- Python 3.11+ recommended
- A Gemini API key available as an environment variable:
  - `GEMINI_API_KEY`

This project uses `uv` (as used in the Boot.dev curriculum), but you can adapt to `pip` if you want.

## Setup

### 1) Install dependencies

Using `uv`:

```bash
uv sync
````

### 2) Provide your API key

Option A: export it in your shell:

```bash
export GEMINI_API_KEY="YOUR_KEY_HERE"
```

Option B: create a `.env` file in the repo root:

```bash
GEMINI_API_KEY=YOUR_KEY_HERE
```

## Run the agent

Basic usage:

```bash
uv run main.py "list files in root"
```

Verbose mode (prints token counts and tool execution details):

```bash
uv run main.py "run tests.py" --verbose
```

## Configuration

Edit `config.py` to change defaults:

* `WORKING_DIR` (sandbox root, default is `./calculator`)
* `MODEL` (Gemini model name)
* `MAX_ITERATIONS` (tool-call loop limit)
* `MAX_CHARS` (file read truncation limit)
* `TIMEOUT` (subprocess execution timeout)

## Notes on safety and limits

This is not meant to be a fully hardened agent. It is intentionally constrained:

* File operations are blocked outside `WORKING_DIR`
* File reads are truncated to avoid flooding the model context
* Python execution uses a timeout

You should still treat “write” and “run” capabilities as risky and keep the sandbox directory small and disposable.

## Development notes

### Adding a new tool

1. Implement the function in `functions/` returning a `str` (success output or `Error: ...`).
2. Define a `types.FunctionDeclaration` schema for it in the same module.
3. Register `(schema, function)` in `tool_registry.py`.

The registry is the only place you should need to touch for tool wiring.

### Testing

Tool functions can be tested via the `test_*.py` scripts:

```bash
uv run test_get_files_info.py
uv run test_get_file_content.py
uv run test_write_file.py
uv run test_run_python_file.py
```

## Troubleshooting

* **`-- API Key Not Found --`**

  * Ensure `GEMINI_API_KEY` is exported or present in `.env`.
* **Tool refuses a path**

  * Tools only accept paths inside `config.WORKING_DIR`.
  * Use relative paths like `main.py`, `pkg/calculator.py`, or `.`.

## License

Educational project. Add a license if you intend to publish/redistribute beyond learning use.
