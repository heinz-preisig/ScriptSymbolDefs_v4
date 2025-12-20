from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, TypedDict
import logging


class GlossaryEntry(TypedDict):
  symbol: str
  description: str
  sort_key: str


@dataclass
class GlossaryFiles:
  nomenclature: Path
  def_vars: Path
  macros: Path
  log: Path


class GlossaryManager:
  def __init__(self, base_dir: Path):
    self.base_dir = Path(base_dir)
    self.files = self._setup_file_paths()
    self.entries: Dict[str, GlossaryEntry] = {}
    self._setup_logging()

  def _setup_file_paths(self) -> GlossaryFiles:
    return GlossaryFiles(
            nomenclature=self.base_dir / 'nomenclature.tex',
            def_vars=self.base_dir / 'defvars.tex',
            macros=self.base_dir / 'macros.tex',
            log=self.base_dir / 'nomenclature.log'
            )

  def _setup_logging(self) -> None:
    logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    self.logger = logging.getLogger(__name__)

  def load(self) -> bool:
    """Load and parse all glossary data."""
    # Check if all required files exist
    required_files = {
        'nomenclature': self.files.nomenclature,
        'def_vars': self.files.def_vars,
        'macros': self.files.macros
    }
    
    missing_files = [name for name, path in required_files.items() if not path.exists()]
    if missing_files:
        missing_str = ", ".join(f"{name}.tex" for name in missing_files)
        self.logger.warning("Missing required files: %s", missing_str)
        return False

    try:
        self.entries = {}  # Clear existing entries
        with self.files.nomenclature.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    self._process_line(line)
        
        self.logger.info("Successfully loaded %d entries", len(self.entries))
        return True
        
    except Exception as e:
        self.logger.error("Error loading glossary: %s", str(e), exc_info=True)
        self.entries = {}  # Clear partial data on error
        return False

  def save(self) -> bool:
    """Save all glossary data back to files."""
    try:
      self._save_nomenclature()
      self._save_def_vars()
      self._save_macros()
      return True
    except Exception as e:
      self.logger.error("Error saving glossary: %s", e, exc_info=True)
      return False

  def _process_line(self, line: str) -> None:
    """Process a single line from the nomenclature file."""
    if not line or line.startswith('%'):
      return

    try:
      hash_name, symbol, description, sort_key = self._parse_line(line)
      self.entries[hash_name] = {
              'symbol'     : symbol,
              'description': description,
              'sort_key'   : sort_key
              }
    except ValueError as e:
      self.logger.warning("Skipping malformed line: %s - %s", line, e)

  def _parse_line(self, line: str) -> tuple[str, str, str, str]:
    """Parse a single line into its components."""
    if not line.startswith(r'\NomenclaturEntry'):
      raise ValueError("Line does not start with \\NomenclaturEntry")

    # Remove the \NomenclaturEntry command
    line = line[len(r'\NomenclaturEntry'):].strip()

    # Handle the case where the first argument is empty
    if line.startswith('{}'):
      line = line[2:].lstrip()  # Remove the empty first argument
    elif line.startswith('{'):
      # Normal case where first argument is not empty
      pass
    else:
      raise ValueError("Invalid format: missing opening brace")

    # Now parse the remaining arguments
    args = []
    current = []
    in_braces = 0

    for char in line:
      if char == '{':
        if in_braces > 0:  # Nested brace
          current.append(char)
        in_braces += 1
      elif char == '}':
        in_braces -= 1
        if in_braces == 0:
          args.append(''.join(current))
          current = []
        else:
          current.append(char)
      elif in_braces > 0:
        current.append(char)

      if len(args) == 4:  # We have all required arguments
        break

    if len(args) != 4:
      raise ValueError(f"Expected 4 arguments, got {len(args)}")

    return tuple(args)

  def _save_nomenclature(self) -> None:
    """Save entries to the nomenclature file."""
    with self.files.nomenclature.open('w', encoding='utf-8') as f:
      for hash_name, entry in sorted(self.entries.items()):
        line = f"\\NomenclaturEntry{{{hash_name}}}{{{entry['symbol']}}}{{{entry['description']}}}{{{entry['sort_key']}}}\n"
        f.write(line)

  def _save_def_vars(self) -> None:
    """Save variable definitions."""
    with self.files.def_vars.open('w', encoding='utf-8') as f:
      for hash_name in sorted(self.entries):
        f.write(f"\\def\\{hash_name}{{\\Var{{{hash_name}}}}}\n")

  def _save_macros(self) -> None:
    """Save macro definitions."""
    with self.files.macros.open('w', encoding='utf-8') as f:
      for hash_name, entry in sorted(self.entries.items()):
        f.write(f"\\def\\{hash_name}{{{{{entry['symbol']}}}}}\n")