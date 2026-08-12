---
name: write-script-directly
description: Write simple scripts directly using write_file with minimal correct content, skipping shell_agent or execution unless testing is explicitly requested.
---

# Write Script Directly

When asked to write a simple script (any language), use `write_file` immediately with the minimal correct content. Do **not** invoke `shell_agent`, run the script, or over-engineer the solution unless the user explicitly asks for execution or testing.

## When to Apply

- User asks to "write", "create", or "generate" a script (e.g., Hello World, a utility function, a config file).
- No explicit request to run, test, or verify the output.

## Steps

1. **Identify the target file path** from the request (e.g., `hello.py`, `greet.sh`).
2. **Write minimal, correct content** using `write_file`.
3. **Confirm the file path** in your response.
4. **Optionally provide execution instructions** as a follow-up hint.

## Example — Hello World in Python

```
write_file(path="hello.py", content='print("Hello, World!")\n')
```

Response to user:
> The file `hello.py` has been created. To run it: `python hello.py`

## Example — Hello World in Bash

```
write_file(path="hello.sh", content='#!/bin/bash\necho "Hello, World!"\n')
```

Response to user:
> The file `hello.sh` has been created. To run it: `bash hello.sh`

## Key Rules

- **Prefer `write_file` over `shell_agent`** for pure write tasks — it is faster, simpler, and avoids unnecessary overhead.
- **Keep content minimal and correct** — no boilerplate beyond what is needed.
- **Do not execute** the script unless the user says "run it", "test it", or "show me the output".
- **Always confirm the file path** so the user knows exactly where the file was written.
- **Provide a run hint** (e.g., `python filename.py`) as a helpful, non-blocking follow-up.