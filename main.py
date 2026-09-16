#!/usr/bin/env encoding=utf-8
import fnmatch
import json
import os
from pathlib import Path

# Hardcoded global fallbacks in case no .gitignore is present
GLOBAL_IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "*.user",
    "bin",
    "obj",
}


def parse_gitignore(gitignore_path: Path) -> list:
    """Parses a .gitignore file and returns a list of clean pattern strings."""
    patterns = []
    if not gitignore_path.exists():
        return patterns

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Normalize trailing slash directories for pattern matching
                if line.endswith("/"):
                    line = line[:-1]
                patterns.append(line)
    except Exception as e:
        print(f"⚠️ Warning: Could not read .gitignore: {e}")

    return patterns


def should_ignore(item: Path, base_path: Path, gitignore_patterns: list) -> bool:
    """Checks if an item matches global ignores or the parsed .gitignore rules."""
    # Always block the core git repository tracking directory
    if item.name == ".git":
        return True

    # 1. Check native global fallbacks first if no explicit rules exist
    if not gitignore_patterns and item.name in GLOBAL_IGNORED_DIRS:
        return True

    # 2. Match against parsed .gitignore rules
    # Get the relative path string from the project root (e.g., 'src/components' or 'log.txt')
    relative_path_str = str(item.relative_to(base_path)).replace(os.sep, "/")
    item_name = item.name

    for pattern in gitignore_patterns:
        # Direct folder/file name match (e.g. 'node_modules' or 'secrets.env')
        if pattern == item_name or pattern == relative_path_str:
            return True
        # Wildcard string matching (e.g. '*.log' or 'build/*')
        if fnmatch.fnmatch(item_name, pattern) or fnmatch.fnmatch(
            relative_path_str, pattern
        ):
            return True
        # Recursive subdirectory rule checks (e.g. 'dist' matching anywhere down the line)
        if "/" not in pattern and any(
            fnmatch.fnmatch(part, pattern)
            for part in Path(relative_path_str).parts
        ):
            return True
        # Contents-only rules (e.g. '**/[Bb]in/*' or 'bin/*') hide everything
        # inside the folder but, unlike a bare 'bin/' rule, don't technically
        # match the folder name itself. A folder whose entire contents are
        # wildcarded away is still just noise in a tree view, so treat the
        # folder as ignored too if this pattern fully empties it.
        if pattern.endswith("/*") and not pattern.endswith("/**/*"):
            folder_pattern = pattern[:-2]  # strip trailing '/*'
            folder_pattern_name = folder_pattern.rsplit("/", 1)[-1]
            if item.is_dir() and (
                fnmatch.fnmatch(item_name, folder_pattern_name)
                or fnmatch.fnmatch(relative_path_str, folder_pattern)
            ):
                return True

    return False


def generate_tree(
    dir_path: Path, base_path: Path, gitignore_patterns: list, prefix: str = ""
) -> list:
    """Recursively walks down directories to build the ASCII tree structure."""
    tree_lines = []

    try:
        # Get all contents and screen them against ignore rules
        items = [
            item
            for item in dir_path.iterdir()
            if not should_ignore(item, base_path, gitignore_patterns)
        ]

        # Sort items: Directories first, then files alphabetically
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return [f"{prefix}└── [Permission Denied]"]

    count = len(items)
    for i, item in enumerate(items):
        is_last = i == count - 1
        connector = "└── " if is_last else "├── "

        tree_lines.append(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            next_prefix = prefix + ("    " if is_last else "│   ")
            tree_lines.extend(
                generate_tree(item, base_path, gitignore_patterns, next_prefix)
            )

    return tree_lines


def generate_tree_dict(
    dir_path: Path, base_path: Path, gitignore_patterns: list
) -> list:
    """Recursively walks down directories to build a nested JSON-serializable structure."""
    entries = []

    try:
        items = [
            item
            for item in dir_path.iterdir()
            if not should_ignore(item, base_path, gitignore_patterns)
        ]
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return [{"name": "[Permission Denied]", "type": "error"}]

    for item in items:
        if item.is_dir():
            entries.append(
                {
                    "name": item.name,
                    "type": "directory",
                    "children": generate_tree_dict(item, base_path, gitignore_patterns),
                }
            )
        else:
            entries.append({"name": item.name, "type": "file"})

    return entries


def prompt_export_formats() -> set:
    """Asks the user which output format(s) they want. Defaults to Markdown."""
    print("\nWhich output format would you like?")
    print("  1) Markdown (.md)  [default]")
    print("  2) JSON (.json)")
    print("  3) Both")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "2":
        return {"json"}
    elif choice == "3":
        return {"md", "json"}
    else:
        return {"md"}


def main():
    print("--- ASCII Directory Tree Generator (with .gitignore parser) ---")
    user_input = input(
        "Enter the directory path to scan (Press Enter for current directory): "
    ).strip()

    if not user_input:
        target_path = Path.cwd()
    else:
        target_path = Path(user_input).expanduser().resolve()

    if not target_path.exists() or not target_path.is_dir():
        print(f"❌ Error: Invalid directory path '{target_path}'")
        return

    folder_name = target_path.name or "root"

    # Read and parse gitignore rules dynamically from target directory root
    gitignore_file = target_path / ".gitignore"
    patterns = parse_gitignore(gitignore_file)

    if patterns:
        print(f"🤖 Found .gitignore! Loaded {len(patterns)} rules.")
    else:
        print("ℹ️ No .gitignore found. Falling back to default script patterns.")

    formats = prompt_export_formats()

    print(f"📂 Scanning: {target_path}")
    print("⏳ Building tree...")

    if "md" in formats:
        output_filename = f"{folder_name}_directory_tree.md"

        tree_structure = [f"{folder_name}/"]
        tree_structure.extend(generate_tree(target_path, target_path, patterns))

        markdown_content = (
            f"# Project Directory Structure: {folder_name}\n\n"
            f"Generated from path: `{target_path}`\n\n"
            "```text\n" + "\n".join(tree_structure) + "\n```\n"
        )

        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"🎉 Success! Tree written to: [ {output_filename} ]")
        except Exception as e:
            print(f"❌ Error writing Markdown file: {e}")

    if "json" in formats:
        output_filename = f"{folder_name}_directory_tree.json"

        tree_data = {
            "root": folder_name,
            "path": str(target_path),
            "tree": generate_tree_dict(target_path, target_path, patterns),
        }

        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(tree_data, f, indent=2, ensure_ascii=False)
            print(f"🎉 Success! Tree written to: [ {output_filename} ]")
        except Exception as e:
            print(f"❌ Error writing JSON file: {e}")


if __name__ == "__main__":
    main()