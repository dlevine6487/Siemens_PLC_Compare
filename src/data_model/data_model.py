class PlcTag:
    def __init__(self, name, data_type, logical_address=None, comment=""):
        self.name, self.data_type, self.logical_address, self.comment = name, data_type, logical_address, comment

class PlcTagTable:
    def __init__(self, name):
        self.name, self.tags = name, []
    def add_tag(self, tag): self.tags.append(tag)

class Pin:
    def __init__(self, name, operand=""):
        self.name, self.operand = name, operand

class Part: # This is our "LadderInstruction"
    def __init__(self, uid, part_type, pins=None):
        self.uid, self.part_type = uid, part_type
        self.pins = pins if pins is not None else []
    def get_operand(self): return self.pins[0].operand if self.pins else ""

class Wire:
    def __init__(self, uid, start_part, start_conn, end_part, end_conn):
        self.uid, self.start_part, self.start_conn, self.end_part, self.end_conn = uid, start_part, start_conn, end_part, end_conn

class Network: # A Network now holds a simple list of parts and wires
    def __init__(self, number, title="", comment=""):
        self.number, self.title, self.comment = number, title, comment
        self.parts = []
        self.wires = []

class InterfaceMember:
    def __init__(self, name, data_type, accessibility="Unspecified", comment=""):
        self.name, self.data_type, self.accessibility, self.comment = name, data_type, accessibility, comment

class BlockInterface:
    def __init__(self):
        self.input_members = []
        self.output_members = []
        self.in_out_members = []
        self.static_members = []
        self.temp_members = []

class PlcBlock:
    def __init__(self, name, block_type, language):
        self.name, self.block_type, self.language = name, block_type, language
        self.interface = BlockInterface()
        self.networks = []
