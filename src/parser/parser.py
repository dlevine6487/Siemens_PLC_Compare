from lxml import etree as ET
import os
from src.data_model.data_model import PlcBlock, Network, Part, Pin, Wire, PlcTagTable, PlcTag

def get_multilingual_text(element, composition_name):
    if element is None: return ""
    text_element = element.find(f".//MultilingualText[@CompositionName='{composition_name}']//Text")
    return text_element.text if text_element is not None and text_element.text is not None else ""

def parse_lad_fbd_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f: xml_content = f.read()

        # This string replacement is brittle. A better solution would be a more robust XML cleanup.
        # For now, it handles the observed newline issues in namespace URIs.
        replacements = {
            'xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5"': 'xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5"',
            'xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5"': 'xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5"',
            'xmlns="http://www.siemens.com/automation/Openness/SW/BlockTypes/v5"': 'xmlns="http://www.siemens.com/automation/Openness/SW/BlockTypes/v5"'
        }
        xml_content = xml_content.replace('Openne\nss', 'Openness').replace('SW/\nInterface', 'SW/Interface').replace('Block\nTypes', 'BlockTypes')

        parser = ET.XMLParser(recover=True, encoding='utf-8')
        root = ET.fromstring(xml_content.encode('utf-8'), parser=parser)
        ns = {'default': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5'}

        block_element = root.find(".//SW.Blocks.FB")
        if block_element is None: block_element = root.find(".//SW.Blocks.FC")
        if block_element is None: block_element = root.find(".//SW.Blocks.OB")
        if block_element is None: return None

        attribute_list = block_element.find("AttributeList")
        # Robustly get the block name
        block_name = get_multilingual_text(attribute_list, "Name")
        if not block_name:
            name_el = attribute_list.find("Name")
            if name_el is not None: block_name = name_el.text

        plc_block = PlcBlock(name=block_name,
                             block_type=block_element.tag.split('.')[-1],
                             language=attribute_list.find("ProgrammingLanguage").text)

        for i, compile_unit in enumerate(block_element.findall(".//SW.Blocks.CompileUnit")):
            network = Network(number=i + 1,
                              title=get_multilingual_text(compile_unit, "Title"),
                              comment=get_multilingual_text(compile_unit, "Comment"))

            flg_net = compile_unit.find(".//NetworkSource/*") # This should find the FlgNet element
            if flg_net is not None:
                for part_element in flg_net.xpath("./default:Parts/*", namespaces=ns):
                    part = Part(uid=part_element.get('UId'), part_type=part_element.get('Name'))
                    for con_element in part_element.findall('Con'):
                        pin_name = con_element.get('Name')
                        operand_components = con_element.xpath(".//Component[@Name]")
                        operand = ".".join(c.get("Name") for c in operand_components)
                        if pin_name: part.pins.append(Pin(name=pin_name, operand=operand))

                    if not part.pins and part.part_type in ['Contact', 'Coil']:
                        operand_components = part_element.xpath(".//Component[@Name]")
                        operand = ".".join(c.get("Name") for c in operand_components)
                        part.pins.append(Pin(name="operand", operand=operand))
                    network.parts.append(part)

                for wire_element in flg_net.xpath("./default:Wires/default:Wire", namespaces=ns):
                    connections = wire_element.getchildren()
                    if len(connections) >= 2:
                        start_node, end_node = connections[0], connections[1]
                        network.wires.append(Wire(uid=wire_element.get('UId'), start_part=start_node.get('UId'),
                                                  start_conn=start_node.get('Name'), end_part=end_node.get('UId'),
                                                  end_conn=end_node.get('Name')))
            plc_block.networks.append(network)
        return plc_block
    except Exception as e:
        print(f"Error parsing LAD/FBD file {file_path}: {e}"); raise

def parse_tag_table_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f: xml_content = f.read()
        xml_content = xml_content.replace('xmlns="http://www.siemens.com/automation/Openness/SW/\\nInterface/v5"','xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5"')
        parser = ET.XMLParser(recover=True, encoding='utf-8')
        root = ET.fromstring(xml_content.encode('utf-8'), parser=parser)
        table_name_element = root.find(".//SW.Tags.PlcTagTable/AttributeList/Name")
        table_name = table_name_element.text if table_name_element is not None else "UnnamedTable"
        tag_table = PlcTagTable(name=table_name)
        for tag_element in root.findall(".//SW.Tags.PlcTag"):
            name, data_type, address, comment = None, None, None, ""
            attribute_list = tag_element.find("AttributeList")
            if attribute_list is not None:
                name_el = attribute_list.find("Name"); datatype_el = attribute_list.find("DataTypeName"); address_el = attribute_list.find("LogicalAddress")
                if name_el is not None: name = name_el.text
                if datatype_el is not None: data_type = datatype_el.text
                if address_el is not None: address = address_el.text
            comment_el = tag_element.find(".//MultilingualText[@CompositionName='Comment']")
            if comment_el is not None:
                text_item = comment_el.find(".//MultilingualTextItem")
                if text_item is not None:
                    text_element = text_item.find("AttributeList/Text")
                    if text_element is not None and text_element.text is not None: comment = text_element.text
            if name:
                tag = PlcTag(name=name, data_type=data_type, logical_address=address, comment=comment)
                tag_table.add_tag(tag)
        return tag_table
    except Exception as e:
        print(f"Error parsing tag table file {file_path}: {e}")
        raise

if __name__ == '__main__':
    # This test block is for verifying the parser's functionality directly.
    import os
    print("--- Testing Parser Module ---")

    # Construct the path to the sample file relative to this script's location
    base_dir = os.path.dirname(__file__)
    sample_file = os.path.abspath(os.path.join(base_dir, '..', '..', 'data', 'PLC_1', 'Program_blocks', 'BoilerAlarm.xml'))

    print(f"Attempting to parse: {sample_file}")

    if not os.path.exists(sample_file):
        print("!!! TEST ERROR: Sample file not found. !!!")
    else:
        try:
            parsed_block = parse_lad_fbd_file(sample_file)
            if parsed_block:
                print("\\n--- PARSE SUCCESS ---")
                print(f"Block Name: {parsed_block.name}")
                print(f"Block Type: {parsed_block.block_type}")
                print(f"Language: {parsed_block.language}")
                print(f"Number of Networks: {len(parsed_block.networks)}")

                total_parts = sum(len(net.parts) for net in parsed_block.networks)
                total_wires = sum(len(net.wires) for net in parsed_block.networks)

                print(f"Total Parts (Instructions): {total_parts}")
                print(f"Total Wires: {total_wires}")

                if parsed_block.networks:
                    net1 = parsed_block.networks[0]
                    print("\\n--- Network 1 Details ---")
                    print(f"  Title: {net1.title}")
                    print(f"  Parts: {len(net1.parts)}")
                    print(f"  Wires: {len(net1.wires)}")

            else:
                print("\\n--- PARSE FAILED: The function returned None. ---")
        except Exception as e:
            print(f"\\n--- PARSE CRASHED: An exception occurred: {e} ---")
            import traceback
            traceback.print_exc()
