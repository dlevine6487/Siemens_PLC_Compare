from lxml import etree as ET
import os
from src.data_model.data_model import PlcBlock, Network, Part, Pin, Wire, PlcTagTable, PlcTag, BlockInterface, InterfaceMember

def get_multilingual_text(element, composition_name):
    if element is None: return ""
    text_element = element.find(f".//MultilingualText[@CompositionName='{composition_name}']//Text")
    return text_element.text if text_element is not None and text_element.text is not None else ""

def parse_lad_fbd_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f: xml_content = f.read()

        xml_content = xml_content.replace('Openne\nss', 'Openness').replace('SW/\nInterface', 'SW/Interface').replace('Block\nTypes', 'BlockTypes')

        parser = ET.XMLParser(recover=True, encoding='utf-8')
        root = ET.fromstring(xml_content.encode('utf-8'), parser=parser)

        ns_flgnet = {'default': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5'}
        ns_if = {'if': 'http://www.siemens.com/automation/Openness/SW/Interface/v5'}

        block_element = root.find(".//SW.Blocks.FB")
        if block_element is None: block_element = root.find(".//SW.Blocks.FC")
        if block_element is None: block_element = root.find(".//SW.Blocks.OB")
        if block_element is None: return None

        attribute_list = block_element.find("AttributeList")
        block_name = get_multilingual_text(attribute_list, "Name") or (attribute_list.find("Name").text if attribute_list.find("Name") is not None else "")

        plc_block = PlcBlock(name=block_name,
                             block_type=block_element.tag.split('.')[-1],
                             language=attribute_list.find("ProgrammingLanguage").text)

        interface_el = attribute_list.find("Interface")
        if interface_el is not None:
            for section_el in interface_el.xpath("if:Sections/if:Section", namespaces=ns_if):
                section_name = section_el.get("Name")
                target_list = None
                if section_name == "Input": target_list = plc_block.interface.input_members
                elif section_name == "Output": target_list = plc_block.interface.output_members
                elif section_name == "InOut": target_list = plc_block.interface.in_out_members
                elif section_name == "Static": target_list = plc_block.interface.static_members
                elif section_name == "Temp": target_list = plc_block.interface.temp_members

                if target_list is not None:
                    for member_el in section_el.findall("if:Member", namespaces=ns_if):
                        comment_text = ""
                        comment_el = member_el.find(".//MultilingualText[@CompositionName='Comment']//Text")
                        if comment_el is not None and comment_el.text is not None: comment_text = comment_el.text
                        member = InterfaceMember(name=member_el.get("Name"), data_type=member_el.get("Datatype"), comment=comment_text)
                        target_list.append(member)

        for i, compile_unit in enumerate(block_element.findall(".//SW.Blocks.CompileUnit")):
            network = Network(number=i + 1,
                              title=get_multilingual_text(compile_unit, "Title"),
                              comment=get_multilingual_text(compile_unit, "Comment"))

            flg_net = compile_unit.find(".//NetworkSource/*")
            if flg_net is not None:
                # --- Final Corrected Robust Operand Parsing Logic ---
                access_map = {
                    acc_el.get('UId'): ".".join(c.get("Name") for c in acc_el.xpath("default:Symbol/default:Component", namespaces=ns_flgnet))
                    for acc_el in flg_net.xpath("./default:Parts/default:Access", namespaces=ns_flgnet)
                }

                part_pins_map = {}
                for wire_el in flg_net.xpath("./default:Wires/default:Wire", namespaces=ns_flgnet):
                    ident_cons = wire_el.xpath("default:IdentCon", namespaces=ns_flgnet)
                    name_cons = wire_el.xpath("default:NameCon", namespaces=ns_flgnet)

                    if ident_cons and name_cons:
                        access_uid = ident_cons[0].get('UId')
                        part_uid = name_cons[0].get('UId')
                        pin_name = name_cons[0].get('Name')

                        if access_uid in access_map:
                            operand = access_map[access_uid]
                            part_pins_map.setdefault(part_uid, {})[pin_name] = operand

                for part_element in flg_net.xpath("./default:Parts/default:Part", namespaces=ns_flgnet):
                    part_uid = part_element.get('UId')
                    part = Part(uid=part_uid, part_type=part_element.get('Name'))

                    if part_uid in part_pins_map:
                        for pin_name, operand in part_pins_map[part_uid].items():
                            part.pins.append(Pin(name=pin_name, operand=operand))

                    network.parts.append(part)
                # --- End of Logic ---

                for wire_element in flg_net.xpath("./default:Wires/default:Wire", namespaces=ns_flgnet):
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

    base_dir = os.path.dirname(__file__)
    sample_file = os.path.abspath(os.path.join(base_dir, '..', '..', 'data', 'PLC_1', 'Program_blocks', 'BoilerAlarm.xml'))

    print(f"Attempting to parse: {sample_file}")

    if not os.path.exists(sample_file):
        print("!!! TEST ERROR: Sample file not found. !!!")
    else:
        try:
            parsed_block = parse_lad_fbd_file(sample_file)
            if parsed_block:
                print("\n--- PARSE SUCCESS ---")
                print(f"Block Name: {parsed_block.name}")

                # --- Test Operand Parsing ---
                print("\n--- Network and Operand Details ---")
                for i, network in enumerate(parsed_block.networks):
                    if not network.parts: continue
                    print(f"\n[Network {i+1}]")
                    for part in network.parts:
                        print(f"  Part: {part.part_type} (UID: {part.uid})")
                        if not part.pins:
                            print("    - No pins found.")
                        for pin in part.pins:
                            print(f"    - Pin: {pin.name}, Operand: '{pin.operand}'")
                # --- End Test ---
            else:
                print("\n--- PARSE FAILED: The function returned None. ---")
        except Exception as e:
            print(f"\n--- PARSE CRASHED: An exception occurred: {e} ---")
            import traceback
            traceback.print_exc()
