from pathlib import Path
from typing import Optional

from PyQt6 import QtCore
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMenu
from PyQt6.QtWidgets import QMessageBox

from directory_history import DirectoryHistory
from editor import Ui_Form
from listview_impl import UI_ListView
from models import GlossaryManager


class UI_EntntiesControl():
  def __init__(self, uis):
    self.items = {"controlRepro"  : uis.groupBoxReproControl,
                  "recordContents": uis.groupBoxRecordContents,
                  "recordControl" : uis.groupBoxRecordControl,
                  # buttons
                  "newRepository" : uis.pushButtonNewRepo,
                  "load"          : uis.pushButtonLoad,
                  "select"        : uis.pushButtonShowList,
                  "edit"          : uis.pushButtonEdit,
                  "new"           : uis.pushButtonNew,
                  "delete"        : uis.pushButtonDelete,
                  "cancel"        : uis.pushButtonCancel,
                  "accept"        : uis.pushButtonAccept,
                  # form
                  "hash"          : uis.lineEditHash,
                  "symbol"        : uis.lineEditSymbol,
                  "description"   : uis.lineEditDescription,
                  "sortKey"       : uis.lineEditSortKey,
                  }

  def show(self, mode):
    for item in self.items:
      self.items[item].setVisible(True)

  def hide(self, mode):
    for item in self.items:
      self.items[item].setVisible(False)

  def control(self, mode):
    visible = []
    hide = []
    if mode == "start":
      visible = ["controlRepro"]
      hide = ["recordContents", "recordControl"]
    elif mode == "select":
      visible = ["controlRepro", "recordControl",
                 "edit", "new", "select"]
      hide = ["recordContents",
              "newRepository",
              "edit","delete","new", "accept", "cancel"]

    elif mode == "edit":
      visible = ["controlRepro", "recordControl",
                 "edit", "new", "delete"]
      hide = ["newRepository", "accept", "cancel"]

    elif mode == "editRecord":
      visible = ["recordControl","recordContents",
                 "cancel", "accept"]
      hide = ["controlRepro",
              "select", "edit", "delete", "new"]

    # elif mode == "cancel":
    #   visible = ["recordControl",
    #              "select"]
    #   hide = ["controlRepro",  "recordContents",
    #           "edit", "new", "delete", "accept", "cancel"]

    for i in visible:
      self.items[i].setVisible(True)
    for i in hide:
      self.items[i].setVisible(False)

  def formEditMode(self, mode):
    self.items["hash"].setReadOnly(not mode)
    self.items["symbol"].setReadOnly(not mode)
    self.items["description"].setReadOnly(not mode)
    self.items["sortKey"].setReadOnly(not mode)
    # self.items["latex"].setEnabled(mode)

    # If switching to view mode, clear any selection
    # if not mode:
    #   self.items["latex"].setCurrentIndex(-1)



class UI(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.glossary: Optional[GlossaryManager] = None
    self.dir_history = DirectoryHistory("glossary_editor")
    self._setup_ui()

  def _setup_ui(self) -> None:
    """Initialize UI components and connections."""
    self.setWindowTitle("Glossary Editor")
    self._new_repository = False

    # Connect buttons
    self.ui.pushButtonNewRepo.clicked.connect(self._create_new_repository)
    self.ui.pushButtonLoad.clicked.connect(self.on_load_clicked)
    self.ui.pushButtonShowList.clicked.connect(self.on_show_list_clicked)
    self.ui.pushButtonNew.clicked.connect(self.on_new_macro_clicked)
    self.ui.pushButtonEdit.clicked.connect(self.on_edit_macro_clicked)
    self.ui.pushButtonDelete.clicked.connect(self.on_delete_macro_clicked)
    self.ui.pushButtonCancel.clicked.connect(self.on_cancel_macro_definition_clicked)
    self.ui.pushButtonAccept.clicked.connect(self.on_accept_macro_clicked)

    # setup interface components
    self._ui_entities = UI_EntntiesControl(self.ui)
    self._ui_entities.control("start")


  def _create_new_repository(self) -> None:
    """Create a new glossary repository with empty files."""
    # Ask user to select a directory
    dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for New Glossary",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
            )

    if not dir_path:
      return  # User cancelled

    dir_path = Path(dir_path)

    # Check if glossary files already exist
    glossary_files = ["nomenclature.tex", "def_vars.tex", "macros.tex"]
    existing_files = [f for f in glossary_files if (dir_path / f).exists()]

    if existing_files:
      QMessageBox.warning(
              self,
              "Glossary Files Exist",
              f"The following glossary files already exist:\n{', '.join(existing_files)}\n\n"
              "Please select a different directory or remove these files."
              )
      return

    try:
      # Create empty glossary files with templates
      files = {
              "nomenclature.tex": r"""% Nomenclature entries
% Format: \nomenclature[<prefix>]{<symbol>}{<description>}
% Example:
\NomenclaturEntry{Area}{A}{area}{A}
""",
              "def_vars.tex"    : r"""% Variable definitions
% Format: \defVar[<unit>]{<name>}{<symbol>}{<description>}
% Example:
\defVar[m^2]{A}{A}{Area}
""",
              "macros.tex"      : r"""% Macro definitions
% Format: \newcommand{\<name>}[<args>]{<definition>}
% Example:
\newcommand{\A}{\Var{A}}
"""
              }

      # Create directory if it doesn't exist
      dir_path.mkdir(parents=True, exist_ok=True)

      # Write files
      for filename, content in files.items():
        (dir_path / filename).write_text(content)

      # Add to recent directories and load the new repository
      self.dir_history.add_directory(str(dir_path))
      self._load_glossary(str(dir_path))

      QMessageBox.information(
              self,
              "Success",
              f"New glossary repository created at {dir_path}"
              )
      self._new_repository = True
      self._ui_entities.control("select")

    except Exception as e:
      QMessageBox.critical(
              self,
              "Error",
              f"Failed to create glossary: {str(e)}"
              )
      self._new_repository = False

  def on_load_clicked(self, dir_path: Optional[str] = None) -> None:
    """Handle load button click.

    Args:
        dir_path: Optional directory path to load directly (used for recent directories)
    """
    if dir_path:
      # Directory was provided (from recent directories)
      self._load_glossary(dir_path)
      self._ui_entities.control("select")
      return

    # Show recent directories in a menu
    recent_dirs = self.dir_history.get_recent_directories()

    if recent_dirs:
      menu = QMenu(self)
      # Add recent directories
      for dir_path in recent_dirs:
        action = menu.addAction(dir_path)
        action.triggered.connect(
                lambda checked, path=dir_path: self.on_load_clicked(path)
                )

      # Add option to browse
      menu.addSeparator()
      browse_action = menu.addAction("Browse...")
      browse_action.triggered.connect(lambda: self._browse_for_directory())

      # Show the menu at the button position
      menu.exec(self.ui.pushButtonLoad.mapToGlobal(
              self.ui.pushButtonLoad.rect().bottomLeft()
              ))
    else:
      # No recent directories, just browse
      self._browse_for_directory()

  def on_show_list_clicked(self) -> None:
    """Handle show list button click.
    
    Shows a list of all entries in the glossary using the list view dialog.
    When an entry is selected, it will be selected in the main form.
    """
    if not self.glossary or not self.glossary.entries:
      QMessageBox.information(self, "No Entries", "No entries available in the glossary.")
      return

    try:
      # Create and show the list view dialog
      self.list_view = UI_ListView(pattern="%s", parent=self)
      self.list_view.build(sorted(self.glossary.entries.keys()))
      self.list_view.newSelection.connect(self._on_macro_selected)
      self.list_view.show()

    except Exception as e:
      QMessageBox.critical(self, "Error", f"Failed to show entry list: {str(e)}")

  def _on_macro_selected(self, macro_name: str) -> None:
    """Handle selection of a macro from the list view.
    
    Args:
        macro_name: The name of the selected macro
    """
    # Populate the form with the selected macro's data
    self._populate_ui(macro_name)
    self.list_view.close()
    self._ui_entities.control("edit")
    self._ui_entities.formEditMode(False)

  def on_new_macro_clicked(self) -> None:
    """Handle new entry button click."""

    if not self._new_repository:
      if not self.glossary:
        QMessageBox.warning(self, "Error", "No glossary is loaded.")
        return

    # Clear the form and prepare for new entry
    self._clear_form()

    # Generate a default sort key (timestamp)
    default_sort_key = QtCore.QDateTime.currentDateTime().toString("yyyyMMddhhmmss")
    self.ui.lineEditSortKey.setText(default_sort_key)

    # Set to edit mode
    self._ui_entities.control("edit")
    self._ui_entities.formEditMode(False)
    self.ui.lineEditHash.setFocus()

    # Store empty original hash to indicate new entry
    self._original_hash = ""

  def on_edit_macro_clicked(self) -> None:
    """Handle edit button click for the current entry."""
    if not self.glossary:
      return

    hash_name = self.ui.lineEditHash.text()
    if not hash_name:
      return

    # Store the original hash in case it gets changed
    self._original_hash = hash_name

    # Switch to edit mode
    self._ui_entities.control("editRecord")
    self._ui_entities.formEditMode(True)

  def on_accept_macro_clicked(self) -> None:
    """Handle accept button click to save the current entry."""
    if not self.glossary:
      return

    # Get the current values from the form
    hash_name = self.ui.lineEditHash.text().strip()
    if not hash_name:
      return

    # Ask for confirmation
    reply = QMessageBox.question(
            self,
            'Confirm Save',
            f'Are you sure you want to save the entry "{hash_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
            )

    if reply == QMessageBox.StandardButton.Yes:
      # Get values from form
      symbol = self.ui.lineEditSymbol.text().strip()
      description = self.ui.lineEditDescription.text().strip()
      sort_key = self.ui.lineEditSortKey.text().strip()

      # Validate inputs
      if not all([symbol, description, sort_key]):
        QMessageBox.warning(self, "Error", "All fields are required.")
        return

      try:
        # Add or update the entry
        self.glossary.entries[hash_name] = {
                'symbol'     : symbol,
                'description': description,
                'sort_key'   : sort_key
                }

        # Save the glossary
        if hasattr(self, '_original_hash') and self._original_hash and self._original_hash != hash_name:
          # If the hash was changed, remove the old entry
          if self._original_hash in self.glossary.entries:
            del self.glossary.entries[self._original_hash]

        # Save to disk
        if self.glossary.save():  # note all changes are updating the file
          # Refresh the UI
          self._populate_ui(hash_name)

          # Switch back to view mode
          self._ui_entities.control("load")
          self._ui_entities.formEditMode(False)
          QMessageBox.information(self, "Success", "Entry saved successfully.")
        else:
          QMessageBox.warning(
                  self,
                  "Error",
                  "Failed to save entry. Check the log for details."
                  )
          self._ui_entities.control("select")

      except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")

  def on_delete_macro_clicked(self) -> None:
    """Handle delete button click for the current entry."""
    if not self.glossary:
      return

    hash_name = self.ui.lineEditHash.text()
    if not hash_name:
      return

    # Ask for confirmation
    reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete the entry "{hash_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
            )

    if reply == QMessageBox.StandardButton.Yes:
      # Delete the entry
      del self.glossary.entries[hash_name]

      # Update the UI
      self._populate_ui()

  def _clear_form(self) -> None:
    """Clear all form fields."""
    self.ui.lineEditHash.clear()
    self.ui.lineEditSymbol.clear()
    self.ui.lineEditDescription.clear()
    self.ui.lineEditSortKey.clear()
    self._ui_entities.formEditMode(False)
    if hasattr(self, '_original_hash'):
      delattr(self, '_original_hash')

  def on_cancel_macro_definition_clicked(self) -> None:
    """Handle cancel button click to exit edit mode and clear or restore form."""
    if hasattr(self, '_original_hash'):
      # If we were creating a new entry, clear the form
      if not self._original_hash:
        self._clear_form()
      # If we were editing an existing entry, restore its values
      elif self._original_hash in self.glossary.entries:
        entry = self.glossary.entries[self._original_hash]
        self.ui.lineEditHash.setText(self._original_hash)
        self.ui.lineEditSymbol.setText(entry['symbol'])
        self.ui.lineEditDescription.setText(entry['description'])
        self.ui.lineEditSortKey.setText(entry['sort_key'])
        self._ui_entities.formEditMode(False)
        delattr(self, '_original_hash')
    else:
      self._clear_form()

    self._ui_entities.control("cancel")

  def _browse_for_directory(self) -> None:
    """Show file dialog to select a directory."""
    default_dir = Path.home() / '.glossaries'
    if not default_dir.exists():
      default_dir = Path.cwd()

    dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Glossary Directory",
            str(default_dir)
            )

    if dir_path:  # User didn't cancel
      self._load_glossary(dir_path)
      self._ui_entities.control("select")

  def _load_glossary(self, dir_path: str) -> None:
    """Load glossary from the specified directory."""
    try:
      self.glossary = GlossaryManager(base_dir=dir_path)
      self.glossary.load()
      self._last_glossary_dir = dir_path  # Store the directory for future use
      self.dir_history.add_directory(dir_path)  # Add this line to save to history
      self._ui_entities.control("load")

    except Exception as e:
      QMessageBox.critical(self, "Error", f"Failed to load glossary: {str(e)}")
      self.glossary = None
      self._ui_entities.control("start")

  def _populate_ui(self, macro_name: str = None) -> None:
    """Populate UI with glossary entries and display the specified macro.
    
    Args:
        macro_name: The name of the macro to display. If None, clears the form.
    """
    if not self.glossary:
      return
      
    if macro_name  in self.glossary.entries:
      # Populate form with the specified macro's data
      macro_data = self.glossary.entries[macro_name]
      self.ui.lineEditHash.setText(macro_name)
      self.ui.lineEditSymbol.setText(macro_data.get('symbol', ''))
      self.ui.lineEditDescription.setText(macro_data.get('description', ''))
      self.ui.lineEditSortKey.setText(macro_data.get('sort_key', ''))
    elif not macro_name and self.glossary.entries:
      # If no macro specified but there are entries, show the first one
      first_macro = next(iter(sorted(self.glossary.entries)))
      macro_data = self.glossary.entries[first_macro]
      self.ui.lineEditHash.setText(first_macro)
      self.ui.lineEditSymbol.setText(macro_data.get('symbol', ''))
      self.ui.lineEditDescription.setText(macro_data.get('description', ''))
      self.ui.lineEditSortKey.setText(macro_data.get('sort_key', ''))

  # def _update_ui_state(self, loaded: bool) -> None:
  #   """Update UI state based on whether a glossary is loaded."""
  #   # Initially hide all buttons except Load and New Repository
  #   self.ui.pushButtonShowList.setVisible(False)
  #   self.ui.pushButtonWrite.setVisible(False)
  #   self.ui.pushButtonNew.setVisible(False)
  #   self.ui.pushButtonEdit.setVisible(False)
  #   self.ui.pushButtonDelete.setVisible(False)
  #   self.ui.pushButtonAccept.setVisible(False)
  #   self.ui.pushButtonCancel.setVisible(False)
  #   self.ui.comboBoxHash.setVisible(False)
  #
  #   # Always show these buttons
  #   self.ui.pushButtonLoad.setVisible(True)
  #   self.ui.pushButtonNewRepo.setVisible(True)
  #
  #   # If a glossary is loaded, show the appropriate buttons
  #   if loaded:
  #     self.ui.pushButtonShowList.setVisible(True)
  #     self.ui.pushButtonNew.setVisible(True)
  #     self.ui.comboBoxHash.setVisible(True)
  #
  #     # Show edit/delete buttons if an entry is selected
  #     if hasattr(self, '_original_hash') or self.ui.comboBoxHash.currentIndex() >= 0:
  #       self.ui.pushButtonEdit.setVisible(True)
  #       self.ui.pushButtonDelete.setVisible(True)
