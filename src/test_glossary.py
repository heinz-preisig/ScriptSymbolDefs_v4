import tempfile
from pathlib import Path
from models import GlossaryManager


def test_glossary_loading():
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create test data
    test_data = r"""\NomenclaturEntry{test1}{T}{Temperature}{T}
\NomenclaturEntry{test2}{P}{Pressure}{P}"""

    # Write test file
    test_file = Path(tmpdir) / 'nomenclature.def'
    test_file.write_text(test_data)

    # Test loading
    manager = GlossaryManager(tmpdir)
    assert manager.load()
    assert len(manager.entries) == 2
    assert 'test1' in manager.entries
    assert manager.entries['test1']['symbol'] == 'T'

    # Test saving
    assert manager.save()
    assert (Path(tmpdir) / 'defvars.def').exists()
    assert (Path(tmpdir) / 'macros.def').exists()