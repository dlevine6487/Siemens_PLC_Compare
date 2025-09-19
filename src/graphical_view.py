from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsLineItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPen, QBrush

class ContactItem(QGraphicsRectItem):
    """A graphical representation of a normally open contact."""
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, 30, 30, parent)
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black))

class CoilItem(QGraphicsRectItem):
    """A graphical representation of a coil."""
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, 30, 30, parent)
        self.setBrush(QBrush(Qt.green))
        self.setPen(QPen(Qt.black))

class GraphicalView(QGraphicsView):
    """
    A view to display a graphical representation of a PLC block.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

    def render_block(self, plc_block):
        """
        Renders a PlcBlock object in the view.
        """
        self.scene.clear()

        y_pos = 0
        for network in plc_block.networks:
            # Simple layout for now: one network per row
            x_pos = 0
            for part in network.parts:
                if 'Contact' in part.part_type:
                    item = ContactItem(x_pos, y_pos)
                    self.scene.addItem(item)
                    x_pos += 40
                elif 'Coil' in part.part_type:
                    item = CoilItem(x_pos, y_pos)
                    self.scene.addItem(item)
                    x_pos += 40

            y_pos += 50

        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
