#!/usr/bin/env python3

import os
import mimetypes
import subprocess
from pathlib import Path

OUTPUT_FILE = "codebase_dump.md"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
EXTENSION_LANG_MAP = {
    "py": "python",
    "ts": "typescript",
    "js": "javascript",
    "sh": "bash",
    "html": "html",
    "css": "css",
    "json": "json",
    "yml": "yaml",
    "yaml": "yaml",
    "c": "c",
    "cpp": "cpp",
    "h": "cpp",
    "java": "java",
    "go": "go",
    "rs": "rust",
    "md": "markdown",
    "txt": "text",
}


def is_git_ignored(file_path):
    result = subprocess.run(["git", "check-ignore", "-q", str(file_path)])
    return result.returncode == 0


def is_text_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type is not None and mime_type.startswith("text")


def get_language(file_path):
    ext = file_path.suffix.lower().lstrip(".")
    return EXTENSION_LANG_MAP.get(ext, ext)


def dump_codebase(start_dir="."):
    start_path = Path(start_dir).resolve()
    output_path = start_path / OUTPUT_FILE
    with open(output_path, "w", encoding="utf-8") as out:
        for file_path in start_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.name == OUTPUT_FILE:
                continue
            if is_git_ignored(file_path):
                continue
            if file_path.stat().st_size > MAX_FILE_SIZE:
                continue
            if not is_text_file(file_path):
                continue

            rel_path = file_path.relative_to(start_path)
            lang = get_language(file_path)
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            out.write("___\n")
            out.write(f"Filename: {rel_path}\n")
            out.write("Content:\n")
            out.write(f"```{lang}\n{content}\n```\n")
            out.write("___\n\n")
    print(f"✅ Dump complete: {output_path}")


if __name__ == "__main__":
    dump_codebase()
