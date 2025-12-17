"""
A module for managing recently used directories with a configuration file.
"""
from pathlib import Path
from typing import Dict, List, Optional
import json

class DirectoryHistory:
    def __init__(self, app_name: str = "glossary_editor", max_entries: int = 10):
        """
        Initialize the directory history manager.
        
        Args:
            app_name: Name of the application (used for config file naming)
            max_entries: Maximum number of recent directories to keep
        """
        self.app_name = app_name
        self.max_entries = max_entries
        self.config_dir = Path.home() / f".config/{app_name}"
        self.config_file = self.config_dir / "directories.json"
        self.recent_dirs: List[str] = []
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load()
    
    def _load(self) -> None:
        """Load the directory history from the config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.recent_dirs = data.get('recent_dirs', [])
            except (json.JSONDecodeError, IOError):
                self.recent_dirs = []
    
    def _save(self) -> None:
        """Save the current directory history to the config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'recent_dirs': self.recent_dirs}, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save
    
    def add_directory(self, directory: str) -> None:
        """
        Add a directory to the history.
        
        Args:
            directory: Path to add to the history
        """
        if not directory:
            return
            
        # Remove if already exists
        if directory in self.recent_dirs:
            self.recent_dirs.remove(directory)
            
        # Add to beginning of list
        self.recent_dirs.insert(0, str(Path(directory).resolve()))
        
        # Trim to max entries
        if len(self.recent_dirs) > self.max_entries:
            self.recent_dirs = self.recent_dirs[:self.max_entries]
            
        self._save()
    
    def get_recent_directories(self) -> List[str]:
        """
        Get the list of recent directories.
        
        Returns:
            List of recent directory paths, most recent first
        """
        return self.recent_dirs.copy()
    
    def clear(self) -> None:
        """Clear the directory history."""
        self.recent_dirs = []
        self._save()
