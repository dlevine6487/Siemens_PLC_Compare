# Siemens PLC Code Viewer

This application is a standalone viewer for Siemens PLC code exported from the TIA Portal. It allows engineers, technicians, and developers to view PLC code in a user-friendly format on a machine where TIA Portal is not installed.

## Features

*   Parses XML files exported from Siemens TIA Portal.
*   Supports viewing of PLC tag tables.
*   Supports viewing of LAD (Ladder Diagram) and FBD (Function Block Diagram) code blocks.
*   Provides a graphical representation of LAD/FBD logic.
*   Features a multi-pane UI with a Project Explorer, a Code Viewer, and a Properties pane.

## How to Run

1.  **Install Dependencies:**
    This project requires Python 3 and the `lxml` and `PyQt5` libraries. You can install the dependencies using pip:
    ```
    pip install lxml PyQt5
    ```

2.  **Run the Application:**
    To run the application, execute the following command from the root of the project directory:
    ```
    python3 -m src.main_window
    ```

## Project Structure

*   `data/`: Contains sample PLC code files for testing.
*   `src/`: Contains the source code for the application.
    *   `main_window.py`: The main application window and UI logic.
    *   `parser.py`: The XML parsing logic.
    *   `data_model.py`: The internal data model for representing PLC code.
    *   `graphical_view.py`: The graphical rendering widget for LAD/FBD.
*   `PLC_Viewer_Analysis.md`: The initial analysis of the project.
*   `SRS_Project_Brief.md`: The Software Requirements Specification for the project.
