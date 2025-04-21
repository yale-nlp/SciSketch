import xml.etree.ElementTree as ET
import re

def find_cell_by_id(tree: ET.Element, id: str) -> ET.Element:
    """
    Find a cell in the diagram by its ID.
    """
    return tree.find(f'.//mxCell[@id="{id}"]')

def update_component_with_image(cell: ET.Element, component_dict: dict) -> ET.Element:
    """
    Update a component in the diagram.
    """
    assert component_dict.get('mime_type') is not None, "Mime type is required"
    assert component_dict.get('base64') is not None, "Encoded image is required"
    assert component_dict.get('value') is not None, "Value is required"
    image_type = component_dict['mime_type']
    base64_image = component_dict['base64']
    image_style = "shape=image;imageAspect=0;aspect=fixed;verticalLabelPosition=bottom;"
    cell.set("style", f"{image_style}image=data:{image_type},{base64_image}")
    # cell.set('value', component_dict['value'])
    cell.set('value', '')
    return cell

def replace_component_by_id(diagram_xml: str, component_dict: dict) -> str:
    """
    Replace a component in a drawio diagram with an image (SVG or local file).
    
    Args:
        diagram_xml (str): The XML content of the drawio diagram
        component_dict (dict): Dictionary containing:
            - id: The mxCell ID to replace
            - source: Either 'svg' or 'author'
            - base64: The base64 encoded image
            - mime_type: The mime type of the image (e.g. 'image/svg+xml')
    
    Returns:
        str: Updated diagram XML with the component replaced
    """
    try:
        root = ET.fromstring(diagram_xml)
        assert component_dict.get('id') is not None, "Component ID is required"

        cell_to_replace = find_cell_by_id(root, component_dict['id'])
        assert cell_to_replace is not None, f"We coudl not find a cell with id {component_dict['id']}"

        updated_cell = update_component_with_image(cell_to_replace, component_dict)

        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    except AssertionError as e:
        print(f"Assertion failed: {e}")
        return diagram_xml
    except Exception as e:
        print(f"Error parsing drawio XML: {e}")
        return diagram_xml

def fix_drawio_xml_special_cells(root: ET.Element) -> None:
    """
    Fix the drawio XML by ensuring all mxCell elements have a parent attribute.
    Args:
        root (ET.Element): the root element of the XML tree
    Returns:
        None
    """
    if root.tag != 'mxGraphModel':
        graph_model = root.find('.//mxGraphModel')
        if graph_model is None:
            print("Invalid diagram: missing mxGraphModel element")
            return
    else:
        graph_model = root
    
    # Find or create root element
    root_element = graph_model.find('./root')

    cell0 = root_element.find('./mxCell[@id="0"]')
    if cell0 is None:
        # Create cell0 and insert at beginning
        cell0 = ET.Element('mxCell', {'id': '0'})
        root_element.insert(0, cell0)
    
    # Check for cell with id="1" and parent="0"
    cell1 = root_element.find('./mxCell[@id="1"]')
    if cell1 is None:
        # Create cell1 and insert after cell0
        cell1 = ET.Element('mxCell', {'id': '1', 'parent': '0'})
        children = list(root_element)
        index = children.index(cell0) if cell0 in children else 0
        root_element.insert(index + 1, cell1)
    elif cell1.get('parent') != '0':
        # Update parent of cell1
        cell1.set('parent', '0')

def fix_drawio_xml_parent_attribute(root: ET.Element) -> None:
    """
    Fix the drawio XML by ensuring all mxCell elements have a parent attribute.

    Args:
        root (ET.Element): the root element of the XML tree

    Returns:
        None
    """
    cells = root.findall(".//mxCell")
    last_parent_id = "1"

    # Process each mxCell
    for cell in cells:
        if cell.attrib.get("id") == "1" and cell.attrib.get("parent") is None:
            cell.set("parent", "0")

        if cell.attrib.get("id") == "0" or cell.attrib.get("id") == "1":
            continue
        # Check if the cell has a parent attribute
        if "parent" not in cell.attrib:
            # Add the parent attribute with the last parent ID
            cell.set("parent", last_parent_id)
        else:
            # Update the last parent ID
            last_parent_id = cell.attrib["parent"]
    return

def fix_nested_objects(root: ET.Element) -> None:
    """
    Fix the drawio XML by ensuring all mxCell elements have a one mxGeometry element.

    Args:
        root (ET.Element): the root element of the XML tree

    Returns:
        None
    """

    # Process all mxCell elements
    for mxcell in root.findall('.//mxCell'):
        geometries = mxcell.findall('./mxGeometry')
        valid_geometry = None

        # Process all geometry elements
        for geometry in geometries:

            # Ensure it has as="geometry" attribute
            if 'as' not in geometry.attrib or geometry.attrib['as'] != 'geometry':
                geometry.set('as', 'geometry')
            
            # Keep the first one we find as valid
            if valid_geometry is None:
                valid_geometry = geometry
            else:
                # Remove extra geometries
                mxcell.remove(geometry)
            
            for child in list(geometry):
                geometry.remove(child)
        
        # Remove all non-mxGeometry children from mxCell
        for child in list(mxcell):
            if child.tag != 'mxGeometry':
                mxcell.remove(child)
    return

def escape_attr_value(match: re.Match) -> str:
    """
    Escape special characters in an XML attribute value.
    """
    attr_name = match.group(1)
    quote = match.group(2)
    value = match.group(3)
    end_quote = match.group(4)
    
    # Replace special characters in sequence
    escaped_value = value

    # Handle ampersand first to avoid double-escaping
    escaped_value = re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', escaped_value)
    
    # Handle other special characters
    escaped_value = escaped_value.replace('<', '&lt;')
    escaped_value = escaped_value.replace('>', '&gt;')
    escaped_value = escaped_value.replace('\\n', '&#xa;')
    
    # Return the full attribute with escaped value
    return f'{attr_name}={quote}{escaped_value}{end_quote}'

def escape_xml_special_chars(xml_string: str) -> str:
    """
    Escape special characters in XML to prevent them from being interpreted as XML tags.
    Args:
        xml_string (str): The XML string to escape
    Returns:
        str: The escaped XML string
    """
    # Process double-quoted attributes
    double_quote_pattern = r'(\w+)=(")(.*?)(")'
    # Apply for double quotes
    fixed_xml = re.sub(double_quote_pattern, escape_attr_value, xml_string)
    return fixed_xml

def fix_drawio_xml(xml_string: str) -> str:
    """
    Fix drawio XML by:
    1. Ensuring all mxCell elements have a parent attribute
    2. Properly escaping XML special characters
    
    Args:
        xml_string (str): The drawio XML string to fix
        
    Returns:
        str: The corrected XML string
    """
    try:
        xml_string = escape_xml_special_chars(xml_string)
        root = ET.fromstring(xml_string)
        fix_drawio_xml_special_cells(root)
        fix_drawio_xml_parent_attribute(root)
        fix_nested_objects(root)
        return ET.tostring(root, encoding='utf-8').decode('utf-8')
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return xml_string
    except Exception as e:
        print(f"Error fixing drawio XML: {e}")
        return xml_string

def find_image_placeholders_with_dimensions(xml_string: str) -> list:
    """
    Find all mxCell elements with image placeholders and extract their dimensions.

    Args:
        xml_string (str): The drawio XML string to search

    Returns:
        list: A list of dictionaries with image value and dimensions
    """
    try:
        root = ET.fromstring(xml_string)
        # Find all mxCell elements with values starting with "[image:"
        image_cells = root.findall('.//*[@style]')
        results = []
        for cell in image_cells:
            value = cell.get('style', '')
            id = cell.get('id', '')
            if 'shape=image' in value:
                # Find the corresponding mxGeometry element directly inside the cell
                geometry = cell.find('./mxGeometry')

                # Extract width and height if geometry was found
                if geometry is not None:
                    width = geometry.get('width')
                    height = geometry.get('height')

                    results.append({
                        'id': id,
                        'value': cell.get('value', ''),
                        'width': width,
                        'height': height
                    })
        return results
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

if __name__ == "__main__":
    xml_string = """<mxfile host="app.diagrams.net">
    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
 
        <mxCell id="topSection & > < &amp;" value="Increasing Model Size" style="text;html=1;strokeColor=none;fillColor=none;fontSize=16;fontStyle=1;" vertex="1">
          <mxGeometry x="20" y="20" width="300" height="30" >
            <mxPoint x="25" y="25" as="offset"/>
            <mxPoint x="25" y="25" as="offset"/>
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
</mxfile>"""
    

    updated_string = fix_drawio_xml(xml_string)
    print(updated_string)
    assert updated_string != xml_string, "The updated string should not be the same as the original string"