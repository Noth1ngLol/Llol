#!/usr/bin/env python3

import argparse
import sys
import os
import json
import logging
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from .cli import CLI
from .config import Config
from .utils import validate_gguf_file, load_default_config, save_config

console = Console()

def setup_logging(debug: bool) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GGUF Metadata Modifier")
    parser.add_argument("file", nargs="?", help="Path to the GGUF file")
    parser.add_argument("-C", "--config", action="store_true", help="Edit configuration")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-e", "--export", help="Export metadata to JSON file")
    parser.add_argument("-i", "--import", dest="import_file", help="Import metadata from JSON file")
    parser.add_argument("-s", "--search", help="Search for a specific metadata key")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser.parse_args()

def load_user_config() -> Dict[str, Any]:
    """Load user configuration or create default if not exists."""
    config_path = os.path.expanduser("~/.gguf_modifier_config.json")
    if not os.path.exists(config_path):
        default_config = load_default_config()
        save_config(config_path, default_config)
        return default_config
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error("Invalid JSON in config file. Using default settings.")
        return load_default_config()

def main() -> None:
    args = parse_arguments()
    setup_logging(args.debug)

    config = Config(debug=args.debug)
    cli = CLI(config)

    try:
        user_config = load_user_config()
        
        if args.config:
            edit_config(user_config)
        elif args.export:
            cli.export_metadata(args.file, args.export)
        elif args.import_file:
            cli.import_metadata(args.file, args.import_file)
        elif args.search:
            cli.search_metadata(args.file, args.search)
        elif args.file:
            process_file(args.file, cli, user_config)
        else:
            show_usage()
    except Exception as e:
        logging.exception("An error occurred:")
        sys.exit(1)

def edit_config(user_config: Dict[str, Any]) -> None:
    """Edit user configuration using the default text editor."""
    config_path = os.path.expanduser("~/.gguf_modifier_config.json")
    editor = os.environ.get('EDITOR', 'nano')
    
    try:
        save_config(config_path, user_config)
        os.system(f"{editor} {config_path}")
        logging.info("Configuration updated successfully.")
    except Exception as e:
        logging.error(f"Failed to edit configuration: {str(e)}")

def process_file(file_path: str, cli: CLI, user_config: Dict[str, Any]) -> None:
    """Process the GGUF file with the given configuration."""
    if not validate_gguf_file(file_path):
        raise ValueError(f"{file_path} is not a valid GGUF file.")
    
    cli.process_file_with_config(file_path, user_config)

def show_usage() -> None:
    """Display usage information."""
    usage_text = Text("Usage:", style="bold")
    usage_text.append("\n\nTo edit configuration:")
    usage_text.append("\n  gguf_modifier -C")
    usage_text.append("\n\nTo process a GGUF file:")
    usage_text.append("\n  gguf_modifier <gguf_file_path>")
    usage_text.append("\n\nTo export metadata:")
    usage_text.append("\n  gguf_modifier -e output.json <gguf_file_path>")
    usage_text.append("\n\nTo import metadata:")
    usage_text.append("\n  gguf_modifier -i input.json <gguf_file_path>")
    usage_text.append("\n\nTo search metadata:")
    usage_text.append("\n  gguf_modifier -s key_name <gguf_file_path>")
    usage_panel = Panel(usage_text, expand=False, border_style="green")
    console.print(usage_panel)

if __name__ == "__main__":
    main()
        
