import subprocess
import json
import logging
from rich.console import Console
from rich.progress import Progress
from .config import Config

console = Console()

class CLI:
    def __init__(self, config: Config):
        self.config = config
        self.rust_binary = "gguf_metadata_modifier"

    def _run_rust_command(self, *args):
        cmd = [self.rust_binary] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing Rust command: {e.stderr}")
            raise RuntimeError(f"Rust command failed: {e.stderr}")

    def modify_metadata(self, file_path: str, key: str, value: str, value_type: str) -> bool:
        try:
            self._run_rust_command("modify", file_path, key, value, value_type)
            console.print(f"[green]Successfully modified metadata: {key}")
            return True
        except RuntimeError as e:
            console.print(f"[red]Failed to modify metadata: {e}")
            return False

    def remove_metadata(self, file_path: str, key: str) -> bool:
        try:
            self._run_rust_command("remove", file_path, key)
            console.print(f"[green]Successfully removed metadata: {key}")
            return True
        except RuntimeError as e:
            console.print(f"[red]Failed to remove metadata: {e}")
            return False

    def export_metadata(self, file_path: str, export_path: str) -> bool:
        try:
            self._run_rust_command("export", file_path, export_path)
            console.print(f"[green]Successfully exported metadata to: {export_path}")
            return True
        except RuntimeError as e:
            console.print(f"[red]Failed to export metadata: {e}")
            return False

    def import_metadata(self, file_path: str, import_path: str) -> bool:
        try:
            self._run_rust_command("import", file_path, import_path)
            console.print(f"[green]Successfully imported metadata from: {import_path}")
            return True
        except RuntimeError as e:
            console.print(f"[red]Failed to import metadata: {e}")
            return False

    def search_metadata(self, file_path: str, search_key: str) -> list:
        try:
            result = self._run_rust_command("search", file_path, search_key)
            metadata = json.loads(result)
            return metadata
        except RuntimeError as e:
            console.print(f"[red]Failed to search metadata: {e}")
            return []

    def process_file_with_config(self, file_path: str, user_config: dict):
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing file...", total=100)

            # Modify existing metadata
            progress.update(task, advance=25, description="Modifying metadata")
            for item in user_config.get('metadata_to_modify', []):
                self.modify_metadata(file_path, item['key'], str(item['value']), item['type'])

            # Add new metadata
            progress.update(task, advance=25, description="Adding new metadata")
            for item in user_config.get('metadata_to_add', []):
                self.modify_metadata(file_path, item['key'], str(item['value']), item['type'])

            # Remove metadata
            progress.update(task, advance=25, description="Removing metadata")
            for key in user_config.get('metadata_to_remove', []):
                self.remove_metadata(file_path, key)

            progress.update(task, advance=25, description="Processing complete")

        console.print("[bold green]File processing completed successfully.")

    def display_metadata(self, metadata: list):
        for item in metadata:
            console.print(f"[bold]Key:[/bold] {item['key']}")
            console.print(f"[bold]Value:[/bold] {item['value']}")
            console.print(f"[bold]Type:[/bold] {item['value_type']}")
            console.print("---")
        
