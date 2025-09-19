import xml.etree.ElementTree as ET
import os

def parse_xml_file(file_path):
    """
    Parses a Siemens TIA Portal XML file and prints the root element tag.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        bool: True if parsing is successful, False otherwise.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        print(f"Successfully parsed {file_path}. Root element: {root.tag}")
        # TODO: Implement detailed parsing logic here.
        # This will involve iterating through the XML tree and extracting
        # relevant information based on the Siemens XML schema.
        return True
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return False
    except ET.ParseError as e:
        print(f"Error: XML parsing failed for {file_path}. Details: {e}")
        return False

if __name__ == "__main__":
    # Example usage with one of the sample files.
    # We assume the script is run from the root of the project.
    sample_file = os.path.join("data", "Default tag table.xml")

    if os.path.exists(sample_file):
        print(f"Attempting to parse {sample_file}...")
        parse_xml_file(sample_file)
    else:
        print(f"Sample file not found at {sample_file}")
        print("Please ensure you are running this script from the root of the project directory.")
