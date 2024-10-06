import os
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
import logging

@dataclass
class MetadataItem:
    key: str
    value: Any
    type: str

@dataclass
class UserConfig:
    metadata_to_modify: list[MetadataItem] = field(default_factory=list)
    metadata_to_add: list[MetadataItem] = field(default_factory=list)
    metadata_to_remove: list[str] = field(default_factory=list)
    default_export_path: str = field(default="./export")
    default_import_path: str = field(default="./import")
    debug: bool = False
    logging_level: str = "INFO"
    max_batch_size: int = 100
    retry_attempts: int = 3
    timeout: float = 30.0

class Config:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.gguf_modifier_config.json")
        self.user_config = self.load_config()
        self.setup_logging()

    def load_config(self) -> UserConfig:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
                return self._dict_to_user_config(config_dict)
            except json.JSONDecodeError:
                logging.error("Invalid JSON in config file. Using default settings.")
        return UserConfig()

    def save_config(self) -> None:
        config_dict = asdict(self.user_config)
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        self._add_comments_to_config()

    def _dict_to_user_config(self, config_dict: Dict[str, Any]) -> UserConfig:
        user_config = UserConfig()
        for key, value in config_dict.items():
            if hasattr(user_config, key):
                if key in ['metadata_to_modify', 'metadata_to_add']:
                    setattr(user_config, key, [MetadataItem(**item) for item in value])
                else:
                    setattr(user_config, key, value)
        return user_config

    def _add_comments_to_config(self) -> None:
        with open(self.config_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        commented_lines = []
        for line in lines:
            commented_lines.append(line)
            if '"key":' in line:
                key = line.split('"')[3]
                comment = self._get_comment_for_key(key)
                if comment:
                    commented_lines.append(f"    // {comment}")
        
        with open(self.config_path, 'w') as f:
            f.write('\n'.join(commented_lines))

    def _get_comment_for_key(self, key: str) -> Optional[str]:
        comments = {
            "metadata_to_modify": "List of metadata items to modify",
            "metadata_to_add": "List of new metadata items to add",
            "metadata_to_remove": "List of metadata keys to remove",
            "default_export_path": "Default path for exporting metadata",
            "default_import_path": "Default path for importing metadata",
            "debug": "Enable debug mode",
            "logging_level": "Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            "max_batch_size": "Maximum number of items to process in a single batch",
            "retry_attempts": "Number of retry attempts for failed operations",
            "timeout": "Timeout for operations in seconds"
        }
        return comments.get(key)

    def setup_logging(self) -> None:
        logging.basicConfig(
            level=getattr(logging, self.user_config.logging_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_metadata_to_modify(self) -> list[MetadataItem]:
        return self.user_config.metadata_to_modify

    def get_metadata_to_add(self) -> list[MetadataItem]:
        return self.user_config.metadata_to_add

    def get_metadata_to_remove(self) -> list[str]:
        return self.user_config.metadata_to_remove

    def get_default_export_path(self) -> str:
        return self.user_config.default_export_path

    def get_default_import_path(self) -> str:
        return self.user_config.default_import_path

    def is_debug_mode(self) -> bool:
        return self.user_config.debug

    def get_max_batch_size(self) -> int:
        return self.user_config.max_batch_size

    def get_retry_attempts(self) -> int:
        return self.user_config.retry_attempts

    def get_timeout(self) -> float:
        return self.user_config.timeout

    def update_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.user_config, key):
                setattr(self.user_config, key, value)
        self.save_config()
        self.setup_logging()  # Re-setup logging in case logging_level was updated

    def reset_to_defaults(self) -> None:
        self.user_config = UserConfig()
        self.save_config()
        self.setup_logging()
