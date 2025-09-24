"""
Configuration Manager for PhoneSync + VideoProcessor
Handles loading and validation of YAML configuration
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str):
        """Initialize with path to config file"""
        self.config_path = Path(config_path)
        self.config = None
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Dict containing configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If required configuration is missing
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file: {e}")

        # Check if config was loaded successfully
        if self.config is None:
            raise ValueError(f"Configuration file is empty or contains only null values: {self.config_path}")

        if not isinstance(self.config, dict):
            raise ValueError(f"Configuration must be a dictionary/object, got {type(self.config).__name__}")

        # Validate required sections
        self._validate_config()
        
        return self.config
    
    def _validate_config(self):
        """Validate that required configuration sections exist"""
        # At this point, we know self.config is not None and is a dict
        assert self.config is not None, "Config should not be None at validation time"
        assert isinstance(self.config, dict), "Config should be a dict at validation time"

        required_sections = [
            'source_folders',
            'target_paths',
            'file_extensions',
            'wudan_rules',
            'ai_settings',
            'logging',
            'options'
        ]

        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate target paths
        target_paths = self.config['target_paths']
        if not isinstance(target_paths, dict):
            raise ValueError("target_paths must be a dictionary")

        required_target_paths = ['pictures', 'videos', 'wudan']
        for path_key in required_target_paths:
            if path_key not in target_paths:
                raise ValueError(f"Missing required target path: {path_key}")

        # Validate file extensions
        file_extensions = self.config['file_extensions']
        if not isinstance(file_extensions, dict):
            raise ValueError("file_extensions must be a dictionary")

        required_extensions = ['pictures', 'videos']
        for ext_key in required_extensions:
            if ext_key not in file_extensions:
                raise ValueError(f"Missing required file extensions: {ext_key}")

        # Validate AI settings
        ai_settings = self.config['ai_settings']
        if not isinstance(ai_settings, dict):
            raise ValueError("ai_settings must be a dictionary")

        required_ai_settings = ['lm_studio_url', 'model', 'kung_fu_prompt']
        for ai_key in required_ai_settings:
            if ai_key not in ai_settings:
                raise ValueError(f"Missing required AI setting: {ai_key}")
    
    def get_source_folders(self) -> list:
        """Get list of source folders to scan"""
        assert self.config is not None, "Config must be loaded before accessing source folders"
        return self.config['source_folders']
    
    def get_target_path(self, path_type: str) -> str:
        """Get target path for specific type (pictures, videos, wudan)"""
        assert self.config is not None, "Config must be loaded before accessing target paths"
        return self.config['target_paths'].get(path_type)

    def get_file_extensions(self, file_type: str) -> list:
        """Get file extensions for specific type (pictures, videos)"""
        assert self.config is not None, "Config must be loaded before accessing file extensions"
        return self.config['file_extensions'].get(file_type, [])

    def is_dry_run(self) -> bool:
        """Check if dry run mode is enabled"""
        assert self.config is not None, "Config must be loaded before accessing options"
        return self.config['options'].get('dry_run', False)

    def is_verbose_logging(self) -> bool:
        """Check if verbose logging is enabled"""
        assert self.config is not None, "Config must be loaded before accessing options"
        return self.config['options'].get('verbose_logging', False)

    def is_deduplication_enabled(self) -> bool:
        """Check if deduplication is enabled"""
        assert self.config is not None, "Config must be loaded before accessing options"
        return self.config['options'].get('enable_deduplication', True)

    def should_create_missing_folders(self) -> bool:
        """Check if missing folders should be created"""
        assert self.config is not None, "Config must be loaded before accessing options"
        return self.config['options'].get('create_missing_folders', True)

    def get_ai_settings(self) -> Dict[str, Any]:
        """Get AI processing settings"""
        assert self.config is not None, "Config must be loaded before accessing AI settings"
        return self.config['ai_settings']

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        assert self.config is not None, "Config must be loaded before accessing logging config"
        return self.config['logging']

    def get_wudan_rules(self) -> Dict[str, Any]:
        """Get Wudan time-based rules"""
        assert self.config is not None, "Config must be loaded before accessing Wudan rules"
        return self.config['wudan_rules']
