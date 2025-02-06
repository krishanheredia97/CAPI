import xml.etree.ElementTree as ET
from xml.dom import minidom
import shlex
import os
from prompt_toolkit.formatted_text import HTML

class XMLManager:
    def __init__(self):
        self.root = ET.Element("root")
        self._current_path = []  # Use underscore prefix for private attribute
        self.depth_colors = [
            '#ff8c00',  # Base orange
            '#ffa64d',  # Lighter orange
            '#ffbf80',  # Even lighter
            '#ffd9b3',  # Very light
            '#ffe6cc',  # Almost white
            '#fff2e6',  # Very light
            '#fff9f2',  # Extremely light
            '#ffffff',  # White
        ]

    @property
    def current_path(self):
        return self._current_path

    def get_prompt(self):
        prompt_parts = []
        if not self._current_path:
            prompt_parts.append(f'<style fg="{self.depth_colors[0]}">root</style>')
        else:
            for i, element in enumerate(self._current_path):
                color = self.depth_colors[min(i, len(self.depth_colors)-1)]
                prompt_parts.append(f'<style fg="{color}">{element.tag}</style>')
        return HTML("> ".join(prompt_parts) + "> ")

    def reset(self):
        self.root = ET.Element("root")
        self._current_path = []

    def _get_current_element(self):
        return self._current_path[-1] if self._current_path else self.root

    def list_tags(self):
        current_element = self._get_current_element()
        if len(current_element) == 0:
            print("No tags found in current location.")
        else:
            print("Available tags:")
            for child in current_element:
                print(f"- {child.tag}")

    def change_tag(self, command):
        tag_name = command[3:].strip()
        if tag_name == "..":
            if self._current_path:
                self._current_path.pop()
                print(f"Moved back to <{self._get_current_element().tag if self._get_current_element() else 'root'}>")
        else:
            current_element = self._get_current_element()
            found = any(child.tag == tag_name for child in current_element)
            if found:
                self._current_path.append(next(child for child in current_element if child.tag == tag_name))
                print(f"Moved to <{tag_name}>")
            else:
                print(f"Error: Tag <{tag_name}> not found.")

    def go_to_root(self):
        self._current_path = []

    def create_element(self, command):
        try:
            full_command = command[3:]
            space_index = full_command.find(' ')
            if space_index == -1:
                tag_name = full_command
                content = None
            else:
                tag_name = full_command[:space_index]
                content = full_command[space_index + 1:].strip()
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]

            if len(self._current_path) >= 8:
                print("Error: Maximum depth of 8 reached.")
                return

            current_element = self._get_current_element()
            new_element = ET.SubElement(current_element, tag_name)
            
            if content:
                # Store content directly without XML parsing
                new_element.text = content
            else:
                new_element.text = "\n"
                
            print(f"Created new tag: <{tag_name}>")
        except Exception as e:
            print(f"Error creating element: {str(e)}")

    def save(self):
        if self.root is None:
            print("Error: No tags to save.")
            return
            
        if len(self.root) == 0:
            print("Error: No tags to save.")
            return
            
        if len(self.root) > 1:
            print("Error: Multiple root tags found. Cannot save.")
            return

        cli_dir = os.path.join(os.getcwd(), "prompting", "cli")
        if not os.path.exists(cli_dir):
            print("Error: 'prompting/cli' directory not found. Run 'capi init' first.")
            return

        file_name = f"{next(iter(self.root)).tag}.xml"
        file_path = os.path.join(cli_dir, file_name)
        
        try:
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(self._pretty_print_xml(self.root))
            print(f"Saved prompt to {file_path}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    
    def show(self):
        current_element = self._get_current_element() if self.current_path else self.root
        if current_element is None:
            return
        print(self._pretty_print_xml(current_element, trunc_max_chars=100))

    def _pretty_print_xml(self, element, trunc_max_chars=None):
        def _escape_text(text):
            if text is None:
                return ""
            return text

        def _format_element(elem, level=0):
            indent = "    " * level
            result = []
            
            # Start tag
            result.append(f"{indent}<{elem.tag}>")
            
            # Handle text content
            if elem.text and elem.text.strip():
                if trunc_max_chars and len(elem.text) > trunc_max_chars:
                    result.append(_escape_text(elem.text[:trunc_max_chars] + "..."))
                else:
                    result.append(_escape_text(elem.text))
            
            # Handle children
            for child in elem:
                result.extend(_format_element(child, level + 1))
                
            # End tag
            result.append(f"{indent}</{elem.tag}>")
            return result

        return "\n".join(_format_element(element))

    def add_terminal_output(self, command: str) -> None:
        from ..term import capture_command_output
        terminal_content = capture_command_output(command)
        current_element = self._get_current_element()
        new_element = ET.SubElement(current_element, "terminal")
        new_element.text = terminal_content
        print(f"Added terminal output to current tag: <{current_element.tag}>")
    
    def add_project_structure(self):
        from ..context import copy_code_context
        import pyperclip
        import re
        
        # Save current clipboard content
        current_content = pyperclip.paste()
        
        # Get the structure content
        copy_code_context('.', False, True, False, 'tree')
        structure_content = pyperclip.paste()
        
        # Restore previous clipboard content
        pyperclip.copy(current_content)
        
        # Extract just the tree structure, removing the XML tags
        tree_content = re.search(r'<project-structure.*?>\s*(.*?)\s*</project-structure>', 
                            structure_content, re.DOTALL)
        if tree_content:
            tree_structure = tree_content.group(1).strip()
            
            # Add the structure to current element
            current_element = self._get_current_element()
            new_element = ET.SubElement(current_element, "project-structure")
            new_element.text = "\n    " + tree_structure + "\n"
            print("Added project structure to current tag")
        else:
            print("Error: Could not extract project structure")
    
    def get_autocomplete_words(self) -> list[str]:
        """Returns a list of available tag names and commands for autocompletion."""
        
        # Get existing tag names from current element
        current = self._get_current_element()
        existing_tags = [child.tag for child in current] if current is not None else []
        
        return existing_tags
    
    def get_full_content(self) -> str:
        return self._pretty_print_xml(self.root, trunc_max_chars=None)

    def edit_with_nano(self):
        import tempfile
        import subprocess
        import os

        current_element = self._get_current_element()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
            # Write current content to temp file if it exists
            if current_element.text:
                temp_file.write(current_element.text)
            temp_file_path = temp_file.name

        try:
            # Open nano editor with the temporary file
            subprocess.run(['nano', temp_file_path])
            
            # Read the edited content
            with open(temp_file_path, 'r') as temp_file:
                new_content = temp_file.read()
                
            # Update the element's content
            current_element.text = new_content
            print(f"Content updated for tag <{current_element.tag}>")
            
        except Exception as e:
            print(f"Error editing content: {str(e)}")
        finally:
            # Clean up - remove temporary file
            os.unlink(temp_file_path)