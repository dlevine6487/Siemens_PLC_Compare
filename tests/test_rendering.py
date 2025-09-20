import sys
import os
import pytest
from PIL import Image, ImageChops
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt

# Add the src directory to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser.parser import parse_lad_fbd_file
from src.graphical_view import NetworkView
from src.data_model.data_model import PlcBlock


def test_render_boiler_alarm():
    """
    Tests the rendering of a specific XML file ('BoilerAlarm.xml') by generating an image.
    This function only handles the generation part. The comparison to a snapshot
    will be added in the next step.
    """
    # Define paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    input_xml = os.path.join(project_root, 'data', 'PLC_1', 'Program_blocks', 'BoilerAlarm.xml')
    output_dir = os.path.join(project_root, 'tests', 'outputs')
    output_path = os.path.join(output_dir, 'boiler_alarm_render.png')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # We need a QApplication instance to work with Qt widgets
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Parse the XML file
    plc_block = parse_lad_fbd_file(input_xml)
    assert plc_block is not None, f"Failed to parse the XML file: {input_xml}"

    # 2. Create the view and render the scene
    view = NetworkView(plc_block)
    scene = view.scene

    # Use the scene's bounding rect to determine the image size
    rect = scene.sceneRect()
    image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
    image.fill(Qt.white)

    painter = QPainter(image)
    scene.render(painter)
    painter.end()

    # 3. Save the image
    assert image.save(output_path), f"Failed to save the rendered image to {output_path}"

    # 4. Compare with snapshot
    snapshot_path = os.path.join(project_root, 'tests', 'snapshots', 'boiler_alarm_render.png')

    if not os.path.exists(snapshot_path):
        # If no snapshot, create it from the current output and fail the test
        os.rename(output_path, snapshot_path)
        pytest.fail(f"Snapshot did not exist. A new snapshot has been created at: {snapshot_path}\n"
                    "Please visually inspect it and commit it to the repository if it is correct.")
    else:
        # If snapshot exists, compare it with the new render
        img_output = Image.open(output_path)
        img_snapshot = Image.open(snapshot_path)

        diff = ImageChops.difference(img_output, img_snapshot)

        assert diff.getbbox() is None, \
            "The rendered image does not match the snapshot. " \
            "Check the `tests/outputs` directory for the new rendering."

        # Clean up the generated output file if the test passes
        os.remove(output_path)
