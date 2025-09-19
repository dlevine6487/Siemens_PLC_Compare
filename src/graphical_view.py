from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem, QGraphicsObject
from PyQt5.QtGui import QPainter, QPen, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from src.data_model.data_model import Part # Import Part for type hinting if needed

class InteractivePartItem(QGraphicsObject):
    partClicked = pyqtSignal(object)
    def __init__(self, part: Part, parent=None):
        super().__init__(parent)
        self.part = part
        self.symbol_pen = QPen(Qt.black, 1.5)
        self.operand_font = QFont("Arial", 8, QFont.Bold)
        self.type_font = QFont("Arial", 8)
        self.pin_font = QFont("Arial", 7)
        self._calculate_geometry()
        self.setFlag(self.ItemIsSelectable, True)

    def _calculate_geometry(self):
        if self.part.part_type in ['Contact', 'Coil']:
            self.item_width, self.item_height = 50, 30
        else:
            fm_type = QFontMetrics(self.type_font)
            self.item_width = max(60, fm_type.horizontalAdvance(self.part.part_type) + 20)
            self.item_height = max(40, (len(self.part.pins) * 15) + 10)

    def boundingRect(self):
        return QRectF(-150, -self.item_height, self.item_width + 300, self.item_height * 2)

    def paint(self, painter, option, widget):
        painter.setPen(self.symbol_pen)
        operand = self.part.get_operand()
        if self.part.part_type == 'Contact':
            painter.setFont(self.operand_font)
            painter.drawText(QRectF(0, -25, 50, 20), Qt.AlignCenter, operand)
            painter.drawLine(0, 0, 15, 0)
            painter.drawLine(15, -10, 15, 10)
            painter.drawLine(35, -10, 35, 10)
            painter.drawLine(35, 0, 50, 0)
        elif self.part.part_type == 'Coil':
            painter.setFont(self.operand_font)
            painter.drawText(QRectF(0, -25, 50, 20), Qt.AlignCenter, operand)
            painter.drawLine(0, 0, 15, 0)
            painter.drawEllipse(15, -10, 20, 20)
            painter.drawLine(35, 0, 50, 0)
        else:
            rect = QRectF(0, -self.item_height / 2, self.item_width, self.item_height)
            painter.drawRect(rect)
            painter.setFont(self.type_font)
            painter.drawText(rect, Qt.AlignCenter, self.part.part_type)
            y_in, y_out = -self.item_height/2 + 5, -self.item_height/2 + 5
            for pin in self.part.pins:
                is_out = pin.name in ['OUT', 'RET_VAL', 'ENO']
                y = y_out if is_out else y_in
                painter.setFont(self.pin_font)
                painter.drawText(QRectF(5, y, self.item_width-10, 15), Qt.AlignRight if is_out else Qt.AlignLeft, pin.name)
                painter.setFont(self.operand_font)
                painter.drawText(QRectF(self.item_width+5, y, 95, 15) if is_out else QRectF(-100, y, 95, 15), Qt.AlignLeft if is_out else Qt.AlignRight, pin.operand)
                if is_out: y_out += 15
                else: y_in += 15

    def mousePressEvent(self, event):
        self.partClicked.emit(self.part)
        super().mousePressEvent(event)

class NetworkView(QGraphicsView):
    properties_signal = pyqtSignal(str)
    def __init__(self, plc_block, parent=None):
        super().__init__(parent)
        self.plc_block, self.scene = plc_block, QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.rail_pen, self.wire_pen = QPen(Qt.black, 2), QPen(Qt.black, 2)
        self.title_font, self.comment_font = QFont("Arial", 10, QFont.Bold), QFont("Arial", 8)
        self.draw_block()

    def handle_part_click(self, part):
        info = f"--- Properties ---\\n\\nType: {part.part_type}\\nUID: {part.uid}\\n\\n--- Pins ---\\n"
        for pin in part.pins: info += f"{pin.name}: {pin.operand}\\n"
        self.properties_signal.emit(info)

    def draw_block(self):
        self.scene.clear()
        y_offset = 0
        for network in self.plc_block.networks:
            y_offset += self.draw_network(network, y_offset) + 50

    def draw_network(self, network, y_offset):
        H_MARGIN, H_SPACING, RUNG_HEIGHT = 20, 30, 100
        current_y = y_offset
        title = QGraphicsTextItem(f"Network {network.number}: {network.title or ''}")
        title.setFont(self.title_font)
        title.setPos(H_MARGIN, current_y)
        self.scene.addItem(title)
        current_y += title.boundingRect().height()

        rung_y = current_y + RUNG_HEIGHT / 2
        rail_x_left, rail_x_right = H_MARGIN, H_MARGIN + 650
        self.scene.addLine(rail_x_left, rung_y - RUNG_HEIGHT/2, rail_x_left, rung_y + RUNG_HEIGHT/2, self.rail_pen)
        self.scene.addLine(rail_x_right, rung_y - RUNG_HEIGHT/2, rail_x_right, rung_y + RUNG_HEIGHT/2, self.rail_pen)

        if not network.parts:
            self.scene.addLine(rail_x_left, rung_y, rail_x_right, rung_y, self.wire_pen)
            return (current_y - y_offset) + RUNG_HEIGHT

        parts_map = {p.uid: p for p in network.parts}
        known_uids = set(parts_map.keys())
        successors = {uid: [] for uid in known_uids}
        predecessors = {uid: [] for uid in known_uids}
        for wire in network.wires:
            if wire.start_part in known_uids and wire.end_part in known_uids:
                successors[wire.start_part].append(wire.end_part)
                predecessors[wire.end_part].append(wire.start_part)

        root_uids = [uid for uid, preds in predecessors.items() if not preds and successors.get(uid)]
        if not root_uids:
            root_uids = [uid for uid in known_uids if not predecessors.get(uid)]
        if not root_uids and network.parts: root_uids = [network.parts[0].uid]

        # Simple linear layout for now
        current_x = rail_x_left
        current_uid = root_uids[0] if root_uids else None

        path_drawn = set()
        while current_uid and current_uid not in path_drawn:
            path_drawn.add(current_uid)
            part = parts_map[current_uid]
            item = InteractivePartItem(part)
            item.partClicked.connect(self.handle_part_click)

            item_x = current_x + H_SPACING
            item.setPos(item_x, rung_y)
            self.scene.addItem(item)
            self.scene.addLine(current_x, rung_y, item_x, rung_y, self.wire_pen)
            current_x = item_x + item.item_width

            next_uids = successors.get(current_uid, [])
            current_uid = next_uids[0] if next_uids else None

        self.scene.addLine(current_x, rung_y, rail_x_right, rung_y, self.wire_pen)
        return (current_y - y_offset) + RUNG_HEIGHT
