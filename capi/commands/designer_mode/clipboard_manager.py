import pyperclip

class ClipboardManager:
    def paste_tag(self, command: str, xml_manager) -> None:
        tag_name = command[6:].strip()
        if not tag_name:
            print("Error: Tag name is required")
            return

        try:
            content = pyperclip.paste()
            xml_manager.create_element(f'nt {tag_name} "{content}"')
            print(f"Created new tag <{tag_name}> with clipboard content")
        except Exception as e:
            print(f"Error accessing clipboard: {str(e)}")
            
    def paste_to_current_tag(self, xml_manager) -> None:
        try:
            current_element = xml_manager._get_current_element()
            content = pyperclip.paste()
            
            # Update the current tag's content
            if current_element is not None:
                # Directly update the text without creating a new element
                current_element.text = content
                print(f"Pasted clipboard content into current tag <{current_element.tag}>")
            else:
                print("Error: No current tag to paste into")
        except Exception as e:
            print(f"Error accessing clipboard: {str(e)}")

    def copy_content(self, xml_manager) -> None:
        try:
            content = xml_manager.get_full_content()
            pyperclip.copy(content)
            print("Copied prompt content to clipboard")
        except Exception as e:
            print(f"Error copying to clipboard: {str(e)}")

    def paste_to_current_tag(self, xml_manager) -> None:
        try:
            # Get the current element directly from the XML manager
            current_element = xml_manager._get_current_element()
            
            if current_element is None:
                print("Error: No current tag to paste into")
                return
                
            # Get clipboard content
            content = pyperclip.paste()
            
            # Directly update the text of the current element
            current_element.text = content
            
            # Print confirmation
            print(f"Pasted clipboard content into current tag <{current_element.tag}>")
        except Exception as e:
            print(f"Error accessing clipboard: {str(e)}")