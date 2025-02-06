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

    def copy_content(self, xml_manager) -> None:
        try:
            content = xml_manager.get_full_content()
            pyperclip.copy(content)
            print("Copied prompt content to clipboard")
        except Exception as e:
            print(f"Error copying to clipboard: {str(e)}")