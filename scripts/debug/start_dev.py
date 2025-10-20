#!/usr/bin/env python3
"""Start development server with .env variables loaded."""

import os
import subprocess  # noqa: S404
from pathlib import Path

# Load .env file
env_file = Path(".env")
if env_file.exists():
    for env_line in env_file.read_text().splitlines():
        env_line = env_line.strip()  # noqa: PLW2901
        if env_line and not env_line.startswith("#") and "=" in env_line:
            key, value = env_line.split("=", 1)
            os.environ[key] = value
            print(f"Loaded: {key}")

# Start uvicorn (trusted local development command)
subprocess.run(  # noqa: S603, S607
    [
        "venv/bin/python",
        "-m",
        "uvicorn",
        "src.api.app:app",
        "--host",
        "0.0.0.0",  # noqa: S104
        "--port",
        "8000",
        "--reload",
    ],
    check=False,
)
