import xml.etree.ElementTree as ET
from typing import Dict, List
import click

def extract_xml_section(response: str, section_tag: str) -> str:
    """Extract specific XML section from response"""
    try:
        root = ET.fromstring(f"<root>{response}</root>")  # Wrap in root for parsing
        section = root.find(section_tag)
        if section is None:
            raise ValueError(f"No '{section_tag}' section found")
        return ET.tostring(section, encoding='unicode', method='text').strip()
    except ET.ParseError as e:
        click.secho(f"Invalid XML format: {str(e)}", fg='red')
        raise
    except Exception as e:
        click.secho(f"XML parsing failed: {str(e)}", fg='red')
        raise