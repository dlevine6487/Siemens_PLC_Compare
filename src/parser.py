from lxml import etree as ET
import os
from src.data_model import PlcTag, PlcTagTable, PlcBlock, Network, Part, Wire

def parse_lad_fbd_file(file_path):
    """
    Parses a Siemens TIA Portal XML file for a LAD/FBD block.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        # Fix for multiline namespace URIs
        xml_content = xml_content.replace('xmlns="http://www.siemens.com/automation/Openness/SW/\nInterface/v5"',
                                          'xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5"')
        xml_content = xml_content.replace('xmlns="http://www.siemens.com/automation/Openne\nss/SW/NetworkSource/FlgNet/v5"',
                                          'xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5"')

        root = ET.fromstring(xml_content.encode('utf-8'))

        ns = {'default': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5'}

        block_element = root.find(".//SW.Blocks.FB")
        if block_element is None:
            block_element = root.find(".//SW.Blocks.FC")
        if block_element is None:
            block_element = root.find(".//SW.Blocks.OB")

        if block_element is None:
            return None

        name_element = block_element.find("AttributeList/Name")
        lang_element = block_element.find("AttributeList/ProgrammingLanguage")
        block_type = block_element.tag.split('.')[-1]

        name = name_element.text if name_element is not None else "Unnamed"
        language = lang_element.text if lang_element is not None else "Unknown"

        plc_block = PlcBlock(name=name, block_type=block_type, language=language)

        for i, compile_unit in enumerate(block_element.findall(".//SW.Blocks.CompileUnit")):
            network = Network(number=i + 1)

            for part_element in compile_unit.xpath(".//default:Parts/*", namespaces=ns):
                part_type = part_element.get('Name')
                if not part_type:
                    name_el = part_element.find("Symbol/Component")
                    if name_el is not None:
                        part_type = name_el.get('Name')

                uid = part_element.get('UId')
                if part_type and uid:
                    part = Part(part_type=part_type, uid=uid)
                    network.parts.append(part)

            for wire_element in compile_unit.xpath(".//default:Wires/default:Wire", namespaces=ns):
                wire_uid = wire_element.get('UId')
                connections = wire_element.getchildren()

                start_part_uid, start_conn_name, end_part_uid, end_conn_name = None, None, None, None

                if len(connections) >= 2:
                    start_node = connections[0]
                    end_node = connections[1]

                    start_part_uid = start_node.get('UId')
                    start_conn_name = start_node.get('Name')
                    end_part_uid = end_node.get('UId')
                    end_conn_name = end_node.get('Name')

                wire = Wire(uid=wire_uid, start_part=start_part_uid, start_conn=start_conn_name,
                            end_part=end_part_uid, end_conn=end_conn_name)
                network.wires.append(wire)

            plc_block.networks.append(network)

        return plc_block

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except ET.XMLSyntaxError as e:
        print(f"Error: XML parsing failed for {file_path}. Details: {e}")
        return None

def parse_tag_table_file(file_path):
    """
    Parses a Siemens TIA Portal XML tag table file into a PlcTagTable object.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        xml_content = xml_content.replace('xmlns="http://www.siemens.com/automation/Openness/SW/\nInterface/v5"',
                                          'xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5"')

        root = ET.fromstring(xml_content.encode('utf-8'))

        table_name_element = root.find(".//SW.Tags.PlcTagTable/AttributeList/Name")
        table_name = table_name_element.text if table_name_element is not None else "UnnamedTable"

        tag_table = PlcTagTable(name=table_name)

        for tag_element in root.findall(".//SW.Tags.PlcTag"):
            name, data_type, address, comment = None, None, None, ""

            attribute_list = tag_element.find("AttributeList")
            if attribute_list is not None:
                name_el = attribute_list.find("Name")
                if name_el is not None:
                    name = name_el.text

                datatype_el = attribute_list.find("DataTypeName")
                if datatype_el is not None:
                    data_type = datatype_el.text

                address_el = attribute_list.find("LogicalAddress")
                if address_el is not None:
                    address = address_el.text

            comment_el = tag_element.find(".//MultilingualText[@CompositionName='Comment']")
            if comment_el is not None:
                text_item = comment_el.find(".//MultilingualTextItem")
                if text_item is not None:
                    text_element = text_item.find("AttributeList/Text")
                    if text_element is not None and text_element.text is not None:
                        comment = text_element.text

            if name:
                tag = PlcTag(name=name, data_type=data_type, logical_address=address, comment=comment)
                tag_table.add_tag(tag)

        return tag_table

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except ET.XMLSyntaxError as e:
        print(f"Error: XML parsing failed for {file_path}. Details: {e}")
        return None

if __name__ == "__main__":
    # Example usage with a tag table file.
    sample_tag_file = os.path.join("data", "Default tag table.xml")
    if os.path.exists(sample_tag_file):
        print(f"--- Parsing Tag Table: {sample_tag_file} ---")
        tag_table_obj = parse_tag_table_file(sample_tag_file)
        if tag_table_obj:
            print(f"Successfully parsed tag table: '{tag_table_obj.name}'")
            print(f"Extracted {len(tag_table_obj.tags)} tags:")
            for tag in tag_table_obj.tags:
                print(f"  - {tag}")
        else:
            print("Failed to parse the tag table.")
        print("-" * 40)

    # Example usage with a LAD/FBD file.
    sample_lad_file = os.path.join("data", "PLC_1", "Program_blocks", "BoilerAlarm.xml")
    if os.path.exists(sample_lad_file):
        print(f"--- Parsing LAD/FBD Block: {sample_lad_file} ---")
        plc_block_obj = parse_lad_fbd_file(sample_lad_file)
        if plc_block_obj:
            print(f"Successfully parsed PLC block: {plc_block_obj}")
            for network in plc_block_obj.networks:
                print(f"  - {network}")
                for part in network.parts:
                    print(f"    - {part}")
                for wire in network.wires:
                    print(f"    - {wire}")
        else:
            print("Failed to parse the PLC block.")
        print("-" * 40)

    else:
        print(f"Sample file not found at {sample_lad_file}")
        print("Please ares running this script from the root of the project directory.")
