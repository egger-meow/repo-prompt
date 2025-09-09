#!/usr/bin/env python3
"""
Repository Prompt Generator
Generates a comprehensive repo_prompt.txt file that provides context about a repository to LLMs.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Set, Dict, Optional
import chardet


class RepoPromptGenerator:
    def __init__(self, root_path: str, config_path: Optional[str] = None):
        """
        Initialize the repository prompt generator.
        
        Args:
            root_path: Path to the repository root
            config_path: Optional path to configuration file
        """
        self.root_path = Path(root_path).resolve()
        self.config = self.load_config(config_path)
        self.ignore_patterns = self.get_ignore_patterns()
        self.binary_extensions = self.get_binary_extensions()
        
    def load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "ignore_dirs": [
                ".git", ".svn", ".hg", "__pycache__", "node_modules", 
                ".idea", ".vscode", "venv", "env", ".env", "dist", 
                "build", "target", ".pytest_cache", ".mypy_cache",
                "repo-prompt"  # Always ignore self
            ],
            "ignore_files": [
                ".DS_Store", "Thumbs.db", "*.pyc", "*.pyo", "*.pyd",
                "*.so", "*.dll", "*.dylib", "*.egg-info", "*.egg",
                "repo_prompt.txt"  # Don't include output in itself
            ],
            "binary_extensions": [
                ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".svg",
                ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                ".zip", ".tar", ".gz", ".rar", ".7z", ".bin", ".exe",
                ".dll", ".so", ".dylib", ".db", ".sqlite", ".pickle", ".pkl"
            ],
            "max_file_size_kb": 500,
            "include_hidden": False,
            "max_depth": 10
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
                
        return default_config
    
    def get_ignore_patterns(self) -> Set[str]:
        """Get combined ignore patterns from config and .gitignore."""
        patterns = set()
        
        # Add patterns from config
        patterns.update(self.config.get("ignore_dirs", []))
        patterns.update(self.config.get("ignore_files", []))
        
        # Try to read .gitignore
        gitignore_path = self.root_path / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.add(line)
            except Exception:
                pass
                
        return patterns
    
    def get_binary_extensions(self) -> Set[str]:
        """Get binary file extensions to skip."""
        return set(self.config.get("binary_extensions", []))
    
    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        name = path.name
        
        # Always ignore repo-prompt directory
        if "repo-prompt" in path.parts:
            return True
            
        # Check if hidden file and config says to exclude
        if not self.config.get("include_hidden", False) and name.startswith('.'):
            return True
            
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            elif pattern.endswith('*') and name.startswith(pattern[:-1]):
                return True
            elif '*' in pattern:
                # Simple glob matching
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return True
            elif name == pattern:
                return True
                
        return False
    
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary based on extension."""
        return file_path.suffix.lower() in self.binary_extensions
    
    def detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(min(4096, file_path.stat().st_size))
                result = chardet.detect(raw)
                return result.get('encoding', 'utf-8') or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def generate_tree(self, start_path: Optional[Path] = None, prefix: str = "", 
                     max_depth: Optional[int] = None, current_depth: int = 0) -> List[str]:
        """Generate directory tree structure."""
        if start_path is None:
            start_path = self.root_path
            
        if max_depth is None:
            max_depth = self.config.get("max_depth", 10)
            
        if current_depth >= max_depth:
            return []
            
        lines = []
        items = []
        
        try:
            for item in sorted(start_path.iterdir()):
                if not self.should_ignore(item):
                    items.append(item)
        except PermissionError:
            return []
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                extension = "    " if is_last else "│   "
                sub_lines = self.generate_tree(
                    item, 
                    prefix + extension, 
                    max_depth, 
                    current_depth + 1
                )
                lines.extend(sub_lines)
                
        return lines
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with proper encoding handling."""
        # Skip binary files
        if self.is_binary_file(file_path):
            return "[Binary file - content not included]"
            
        # Check file size
        try:
            size_kb = file_path.stat().st_size / 1024
            max_size = self.config.get("max_file_size_kb", 500)
            if size_kb > max_size:
                return f"[File too large - {size_kb:.1f}KB exceeds {max_size}KB limit]"
        except Exception:
            return "[Could not read file]"
            
        # Try to read file
        encoding = self.detect_encoding(file_path)
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"
    
    def collect_files(self, start_path: Optional[Path] = None) -> List[Path]:
        """Recursively collect all files to include."""
        if start_path is None:
            start_path = self.root_path
            
        files = []
        
        def walk_dir(path: Path, depth: int = 0):
            if depth >= self.config.get("max_depth", 10):
                return
                
            try:
                for item in sorted(path.iterdir()):
                    if self.should_ignore(item):
                        continue
                        
                    if item.is_file():
                        files.append(item)
                    elif item.is_dir():
                        walk_dir(item, depth + 1)
            except PermissionError:
                pass
        
        walk_dir(start_path)
        return files
    
    def generate_prompt(self, output_path: Optional[str] = None) -> str:
        """Generate the complete repository prompt."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("REPOSITORY CONTEXT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Repository: {self.root_path.name}")
        lines.append(f"Path: {self.root_path}")
        lines.append("")
        
        # Directory structure
        lines.append("=" * 80)
        lines.append("DIRECTORY STRUCTURE")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"{self.root_path.name}/")
        tree_lines = self.generate_tree()
        lines.extend(tree_lines)
        lines.append("")
        
        # File contents
        lines.append("=" * 80)
        lines.append("FILE CONTENTS")
        lines.append("=" * 80)
        lines.append("")
        
        files = self.collect_files()
        for file_path in files:
            relative_path = file_path.relative_to(self.root_path)
            
            lines.append("-" * 80)
            lines.append(f"File: {relative_path}")
            lines.append("-" * 80)
            
            content = self.read_file_content(file_path)
            if content is not None:
                lines.append(content)
            lines.append("")
        
        # Additional context
        lines.append("=" * 80)
        lines.append("ADDITIONAL CONTEXT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("This repository structure and content has been provided to give you ")
        lines.append("comprehensive context about the project. Please use this information ")
        lines.append("to better understand the codebase and provide more accurate assistance.")
        lines.append("")
        
        # Statistics
        lines.append("Statistics:")
        lines.append(f"- Total files included: {len(files)}")
        lines.append(f"- Repository root: {self.root_path}")
        lines.append("")
        
        prompt_text = "\n".join(lines)
        
        # Save to file if output path provided
        if output_path:
            output_file = Path(output_path)
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(prompt_text)
                print(f"Repository prompt saved to: {output_file}")
            except Exception as e:
                print(f"Error saving prompt to file: {e}")
                
        return prompt_text


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive repository prompt for LLMs"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output",
        default="repo_prompt.txt",
        help="Output file path (default: repo_prompt.txt)"
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print to stdout instead of saving to file"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = RepoPromptGenerator(args.path, args.config)
    
    # Generate prompt
    if args.no_save:
        prompt = generator.generate_prompt()
        print(prompt)
    else:
        generator.generate_prompt(args.output)
        print(f"\nRepository prompt has been generated successfully!")
        print(f"Output file: {args.output}")
        print(f"\nYou can now copy the contents of '{args.output}' and paste it into any LLM chat")
        print("to provide comprehensive context about your repository.")


if __name__ == "__main__":
    main()
