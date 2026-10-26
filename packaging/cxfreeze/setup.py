"""cx_Freeze setup script for building Answer."""

import sys
import os
from cx_Freeze import setup, Executable

# Application info
APP_NAME = "Answer"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Generate datasets from documents using AI APIs"
APP_AUTHOR = "Articipate"
APP_COPYRIGHT = "Copyright (c) 2026 Articipate"

# Dependencies to include
build_exe_options = {
    "packages": [
        "answer_dataset",
        "PySide6",
        "httpx",
        "pydantic",
        "pypdf",
        "docx",
        "openpyxl",
        "tiktoken",
        "jsonschema",
        "json_repair",
        "keyring",
        "platformdirs",
        "yaml",
        "aiofiles",
    ],
    "includes": [],
    "excludes": [
        "tkinter",
        "unittest",
        "email",
        "html",
        "xml",
        "pydoc",
        "doctest",
    ],
    "include_files": [
        (os.path.join("..", "..", "logos", "Answer_Logo.png"), "logos/Answer_Logo.png"),
        (os.path.join("..", "..", "Answer_Logo.png"), "Answer_Logo.png"),
    ],
    "zip_include_packages": ["encodings", "PySide6"],
    "zip_exclude_packages": [],
}

# Base for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # GUI application, no console window

executables = [
    Executable(
        script=os.path.join("..", "..", "src", "answer_dataset", "app.py"),
        base=base,
        target_name="Answer" if sys.platform == "win32" else "Answer",
        icon=None,
    )
]

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={"build_exe": build_exe_options},
    executables=executables,
)
