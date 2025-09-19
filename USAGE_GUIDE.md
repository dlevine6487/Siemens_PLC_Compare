# Usage Guide: Siemens PLC Code Viewer

## Introduction

This guide provides step-by-step instructions on how to use the Python files in the Siemens PLC Code Viewer project. It covers setting up the environment, running the main application, and using the parsing modules as a standalone library.

---

## 1. Setting up the Environment

### Prerequisites

*   Python 3.6 or higher.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**
    The project requires the `lxml` and `PyQt5` libraries. You can install them using pip:
    ```bash
    pip install lxml PyQt5
    ```

---

## 2. Running the PLC Code Viewer Application

The main entry point for the GUI application is `src/main_window.py`.

### Step-by-step Instructions

1.  **Navigate to the project's root directory** in your terminal.

2.  **Run the main window module:**
    ```bash
    python3 -m src.main_window
    ```

3.  The **Siemens PLC Code Viewer** window will open.

### Understanding the UI

*   **Project Explorer (Left Pane):** This pane shows a tree view of the project's `data` directory. You can navigate the folders and see the available XML and other source files.
*   **Code Viewer (Center Pane):** This is the main area where the content of the selected file is displayed. It can show tag tables in a tabular format or a graphical representation of LAD/FBD blocks.
*   **Properties (Right Pane):** This pane is intended to show detailed properties of a selected element in the code viewer (this feature is not fully implemented yet).
*   **Menu Bar:**
    *   **File > Open:** Allows you to open a single XML file using a file dialog.
    *   **File > Exit:** Closes the application.
*   **Status Bar:** Displays messages about the application's status, such as when a file is opened or if an error occurs.

### How to View Files

*   **Using the Menu:**
    1.  Go to `File > Open`.
    2.  A file dialog will appear. Navigate to the `data` directory and select an XML file.
    3.  The file will be parsed, and its content will be displayed in the central code viewer.
*   **Using the Project Explorer:**
    1.  In the Project Explorer pane, navigate to the desired file.
    2.  Double-click on the file name.
    3.  The file will be parsed and displayed.

---

## 3. Using the Parser as a Standalone Library

The parsing logic is contained in `src/parser.py`. You can import the functions from this module into your own Python scripts to programmatically parse PLC code files.

### Parsing a Tag Table

The `parse_tag_table_file` function parses a tag table XML file and returns a `PlcTagTable` object.

**Example:**
```python
from src.parser import parse_tag_table_file
from src.data_model import PlcTagTable, PlcTag

# Path to the tag table file
file_path = "data/Default tag table.xml"

# Parse the file
tag_table = parse_tag_table_file(file_path)

if tag_table:
    print(f"Parsed tag table: {tag_table.name}")
    for tag in tag_table.tags:
        print(f"  - Tag: {tag.name}, Type: {tag.data_type}, Address: {tag.logical_address}")
```

### Parsing a LAD/FBD Block

The `parse_lad_fbd_file` function parses an XML file for a LAD or FBD block and returns a `PlcBlock` object.

**Example:**
```python
from src.parser import parse_lad_fbd_file
from src.data_model import PlcBlock

# Path to the block file
file_path = "data/PLC_1/Program_blocks/BoilerAlarm.xml"

# Parse the file
plc_block = parse_lad_fbd_file(file_path)

if plc_block:
    print(f"Parsed block: {plc_block.name}")
    print(f"  - Type: {plc_block.block_type}")
    print(f"  - Language: {plc_block.language}")
    for network in plc_block.networks:
        print(f"    - Network {network.number} with {len(network.parts)} parts and {len(network.wires)} wires.")
```

---

## 4. Understanding the Data Model

The data model classes are defined in `src/data_model.py`. They provide a structured, object-oriented representation of the parsed PLC code.

*   `PlcTag`: Represents a single tag with attributes like `name`, `data_type`, `logical_address`, and `comment`.
*   `PlcTagTable`: A container for a list of `PlcTag` objects.
*   `PlcBlock`: A base class for PLC blocks (FB, FC, OB) with attributes like `name`, `block_type`, `language`, and lists for `interface` and `networks`.
*   `Network`: Represents a single network within a block, containing lists of `parts` and `wires`.
*   `Part`: Represents a graphical element in a network, such as a contact or a coil.
*   `Wire`: Represents a wire connecting two `Part` objects.
