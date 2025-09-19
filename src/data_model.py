class PlcTag:
    """
    Represents a single PLC tag in a vendor-neutral way.

    Attributes:
        name (str): The name of the tag.
        data_type (str): The data type of the tag (e.g., 'Bool', 'Int').
        logical_address (str): The logical address of the tag (e.g., '%I0.0').
        comment (str): The comment associated with the tag.
    """
    def __init__(self, name, data_type, logical_address, comment=""):
        self.name = name
        self.data_type = data_type
        self.logical_address = logical_address
        self.comment = comment

    def __repr__(self):
        return (f"PlcTag(name='{self.name}', data_type='{self.data_type}', "
                f"logical_address='{self.logical_address}', comment='{self.comment}')")


class PlcTagTable:
    """
    Represents a collection of PLC tags from a single tag table.

    Attributes:
        name (str): The name of the tag table.
        tags (list): A list of PlcTag objects in the table.
    """
    def __init__(self, name):
        self.name = name
        self.tags = []

    def add_tag(self, tag):
        """Adds a PlcTag object to the table."""
        if isinstance(tag, PlcTag):
            self.tags.append(tag)
        else:
            raise TypeError("Only PlcTag objects can be added to a PlcTagTable.")

    def __repr__(self):
        return f"PlcTagTable(name='{self.name}', tags_count={len(self.tags)})"


class PlcBlock:
    """
    Base class for a PLC block (e.g., FB, FC, OB).

    Attributes:
        name (str): The name of the block.
        block_type (str): The type of the block (e.g., 'FB', 'FC', 'OB').
        language (str): The programming language of the block (e.g., 'LAD', 'FBD').
        interface (dict): A dictionary representing the block's interface.
        networks (list): A list of Network objects in the block.
    """
    def __init__(self, name, block_type, language):
        self.name = name
        self.block_type = block_type
        self.language = language
        self.interface = {}  # E.g., {'Input': [], 'Output': [], ...}
        self.networks = []

    def __repr__(self):
        return (f"PlcBlock(name='{self.name}', type='{self.block_type}', "
                f"language='{self.language}', networks={len(self.networks)})")

class Network:
    """
    Represents a network within a PLC block.

    Attributes:
        number (int): The network number.
        parts (list): A list of Part objects in the network.
        wires (list): A list of Wire objects in the network.
    """
    def __init__(self, number):
        self.number = number
        self.parts = []
        self.wires = []

    def __repr__(self):
        return f"Network(number={self.number}, parts={len(self.parts)}, wires={len(self.wires)})"

class Part:
    """
    Represents a part in a network (e.g., a contact, coil, or function call).

    Attributes:
        part_type (str): The type of the part (e.g., 'Contact', 'Coil').
        uid (str): The unique ID of the part within the network.
        connections (dict): A dictionary of connection points for the part.
    """
    def __init__(self, part_type, uid):
        self.part_type = part_type
        self.uid = uid
        self.connections = {}

    def __repr__(self):
        return f"Part(type='{self.part_type}', uid={self.uid})"

class Wire:
    """
    Represents a wire connecting parts in a network.

    Attributes:
        uid (str): The unique ID of the wire.
        start_part (str): The UID of the part where the wire starts.
        start_conn (str): The name of the connection point on the start part.
        end_part (str): The UID of the part where the wire ends.
        end_conn (str): The name of the connection point on the end part.
    """
    def __init__(self, uid, start_part, start_conn, end_part, end_conn):
        self.uid = uid
        self.start_part = start_part
        self.start_conn = start_conn
        self.end_part = end_part
        self.end_conn = end_conn

    def __repr__(self):
        return (f"Wire(uid={self.uid}, from='{self.start_part}:{self.start_conn}', "
                f"to='{self.end_part}:{self.end_conn}')")
