# Repo Prompt Generator

A powerful tool to generate comprehensive repository context files (`repo_prompt.txt`) for sharing with Large Language Models (LLMs). This tool helps LLMs understand your entire project structure and codebase by providing a well-formatted overview of your repository.

## Why Use This Tool?

Most LLM services are web-based and don't have direct access to your local repository. When asking questions about your code, the LLM lacks context about your project structure, file contents, and relationships between components. This tool solves that problem by generating a single text file containing:

- Complete directory tree structure
- Full content of all relevant source files
- Automatic filtering of binary files and common ignore patterns
- Configurable exclusion rules

## Features

- 🌳 **Visual Directory Tree**: Generates a clean, ASCII-art style directory structure
- 📄 **Smart File Reading**: Automatically detects and handles different file encodings
- 🚫 **Intelligent Filtering**: Excludes binary files, build artifacts, and version control directories
- ⚙️ **Highly Configurable**: Customize ignore patterns, file size limits, and directory depth
- 🎯 **Self-Aware**: Automatically excludes itself (`repo-prompt` directory) from the output
- 📊 **File Statistics**: Provides summary statistics about the included files

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository to your local machine:
```bash
git clone <repository-url> repo-prompt
cd repo-prompt
```

2. Install the required dependency:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install chardet
```

## Usage

### Basic Usage

Navigate to any repository and run:

```bash
python path/to/repo_prompt_generator.py
```

This will generate a `repo_prompt.txt` file in the current directory.

### Advanced Usage

```bash
# Generate prompt for a specific directory 
python repo_prompt_generator.py /path/to/your/repository

# Specify custom output file
python repo_prompt_generator.py -o my_repo_context.txt

# Use a custom configuration file
python repo_prompt_generator.py -c custom_config.json

# Print to console instead of saving to file
python repo_prompt_generator.py --no-save
```

### Command Line Arguments

- `path`: Path to the repository (default: current directory)
- `-o, --output`: Output file path (default: `repo_prompt.txt`)
- `-c, --config`: Path to custom configuration file
- `--no-save`: Print output to console instead of saving to file

## Configuration

The tool can be customized using a JSON configuration file. Here's the default configuration:

```json
{
  "ignore_dirs": [
    ".git", ".svn", "__pycache__", "node_modules", 
    ".idea", ".vscode", "venv", "env", "dist", 
    "build", "repo-prompt"
  ],
  "ignore_files": [
    ".DS_Store", "*.pyc", "*.log", "repo_prompt.txt"
  ],
  "binary_extensions": [
    ".jpg", ".png", ".pdf", ".zip", ".exe", ".dll"
  ],
  "max_file_size_kb": 500,
  "include_hidden": false,
  "max_depth": 10
}
```

### Configuration Options

- **`ignore_dirs`**: List of directory names to exclude
- **`ignore_files`**: List of file patterns to exclude (supports wildcards)
- **`binary_extensions`**: File extensions to treat as binary (content will be skipped)
- **`max_file_size_kb`**: Maximum file size in KB to include (larger files will be noted but content skipped)
- **`include_hidden`**: Whether to include hidden files (starting with `.`)
- **`max_depth`**: Maximum directory depth to traverse

## Example Output

The generated `repo_prompt.txt` file will have the following structure:

```
================================================================================
REPOSITORY CONTEXT
================================================================================

Repository: YourProjectName
Path: /full/path/to/repository

================================================================================
DIRECTORY STRUCTURE
================================================================================

YourProjectName/
├── src/
│   ├── main.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config.py
├── tests/
│   └── test_main.py
├── README.md
└── requirements.txt

================================================================================
FILE CONTENTS
================================================================================

--------------------------------------------------------------------------------
File: src/main.py
--------------------------------------------------------------------------------
[actual file content here]

--------------------------------------------------------------------------------
File: src/utils/helpers.py
--------------------------------------------------------------------------------
[actual file content here]

[... more files ...]

================================================================================
ADDITIONAL CONTEXT
================================================================================

Statistics:
- Total files included: 15
- Repository root: /full/path/to/repository
```

## How to Use with LLMs

1. Run the tool in your repository:
   ```bash
   python repo_prompt_generator.py
   ```

2. Open the generated `repo_prompt.txt` file

3. Copy the entire content

4. Paste it at the beginning of your conversation with any LLM (ChatGPT, Claude, Gemini, etc.)

5. Ask your questions about the codebase - the LLM now has full context!

## Tips for Best Results

1. **Clean Your Repository**: Run the tool after cleaning build artifacts and temporary files for a cleaner output

2. **Customize Ignores**: Add project-specific ignore patterns to exclude test data, documentation, or other non-essential files

3. **Size Management**: For large repositories, adjust `max_file_size_kb` and `max_depth` to keep the output manageable

4. **Update Regularly**: Regenerate the prompt file when making significant changes to your codebase

5. **Version Control**: Consider adding `repo_prompt.txt` to `.gitignore` since it can be regenerated anytime

## Troubleshooting

### Common Issues

**Issue**: "File too large" messages
- **Solution**: Adjust `max_file_size_kb` in the configuration

**Issue**: Important files are being ignored
- **Solution**: Check and modify the `ignore_dirs` and `ignore_files` patterns in the configuration

**Issue**: Binary file content showing as garbled text
- **Solution**: Add the file extension to `binary_extensions` in the configuration

**Issue**: Encoding errors
- **Solution**: The tool automatically detects encoding, but you can report issues with specific files

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Support

If you encounter any problems or have suggestions, please open an issue on the repository.
