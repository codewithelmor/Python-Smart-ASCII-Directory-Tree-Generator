# 📂 Smart ASCII Directory Tree Generator

A lightweight, zero-dependency Python tool that recursively crawls any given directory, respects its native `.gitignore` configuration rules, and renders the layout into a clean ASCII tree — exportable as Markdown, JSON, or both.

The generated outputs are dynamically matched and named directly after your scanned root folder (e.g., `<project-folder-name>_directory_tree.md` / `<project-folder-name>_directory_tree.json`).

## ✨ Features

- **🤖 Smart `.gitignore` Integration**: Automatically checks for, parses, and implements file/folder exclusions declared inside a local `.gitignore` line by line.
- **📂 Folder-First Ordering**: Renders directories grouped cleanly above single files alphabetically.
- **⚙️ Standalone Global Exclusions**: Drops structural junk elements like `.git/` automatically, and relies on built-in presets (like `node_modules/`, `venv/`, and `.vscode/`) if no explicit `.gitignore` is found.
- **🛡️ Permission Handling**: Gracefully maps blocked system folders with a clear marker tag without throwing runtime process crashes.
- **📤 Dual Export Formats**: Choose Markdown, JSON, or both at runtime — same naming convention across formats.
- **📦 Zero External Packages**: Powered purely by standard native Python components (`pathlib`, `fnmatch` & `json`).

## 🚀 Getting Started

### Prerequisites

- **Python 3.6** or higher installed.

### Run & Use

1. Place `main.py` into your working folder.
2. Open your terminal or shell window and run:
   ```bash
   python main.py
   ```
3. **Specify the target**: Paste an absolute/relative directory path or press `Enter` to map the workspace directory where the script execution takes place.
4. **Choose your export format**: When prompted, select:
   - `1` for Markdown only *(default)*
   - `2` for JSON only
   - `3` for both Markdown and JSON

## 📊 Example Output

If you scan a project named **`core-api`** containing a `.gitignore` blocking `*.log` and `build/`, choosing Markdown produces a file named **`core-api_directory_tree.md`**:

```text
core-api/
├── .gitignore
├── README.md
├── main.py
├── config/
│   ├── settings.json
│   └── tokens.json
└── src/
    ├── database.py
    └── utils.py
```

Choosing JSON produces **`core-api_directory_tree.json`** with the same structure, nested:

```json
{
  "root": "core-api",
  "path": "/absolute/path/to/core-api",
  "tree": [
    {
      "name": "config",
      "type": "directory",
      "children": [
        { "name": "settings.json", "type": "file" },
        { "name": "tokens.json", "type": "file" }
      ]
    },
    {
      "name": "src",
      "type": "directory",
      "children": [
        { "name": "database.py", "type": "file" },
        { "name": "utils.py", "type": "file" }
      ]
    },
    { "name": ".gitignore", "type": "file" },
    { "name": "README.md", "type": "file" },
    { "name": "main.py", "type": "file" }
  ]
}
```

Selecting "Both" writes out `core-api_directory_tree.md` and `core-api_directory_tree.json` in the same run.

## ⚙️ How Exclusions Work

- **With `.gitignore`**: The script parses comments, skips empty rows, strips directory trailing slashes, and respects explicit glob match strings (e.g., `*.exe`, `temp/*`, `dist`).
- **Without `.gitignore`**: The script falls back to an internal predefined block list of common language and IDE footprints: `.git`, `node_modules`, `__pycache__`, `venv`, `.venv`, `.idea`, and `.vscode`.

## 📄 License

This utility is completely open-source and free to distribute or alter under the [MIT License](LICENSE).
