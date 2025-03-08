from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import clear
from .xml_manager import XMLManager
from .tag_completer import TagCompleter
from .clipboard_manager import ClipboardManager
from prompt_toolkit.styles import Style 
from ..session_manager import SessionManager
from ..file_browser_mode.file import handle_file

class PromptManager:
    def __init__(self):
        self.xml_manager = XMLManager()
        self.clipboard_manager = ClipboardManager()
        self.session = PromptSession()
        self.style = self.create_style()
        self.completer = TagCompleter(self.xml_manager.get_autocomplete_words)
        self.session_manager = SessionManager()

    def create_style(self):
        return Style.from_dict({
            'prompt': '#ff8c00 bold',
            'path': '#ffa64d',
        })

    def run(self):
        print("🔨 Prompt Designer Mode")
        print("Available commands: nt <tag-name> [\"content\"], paste <tag-name>, ct <tag-name>, ls, show, prompt, cls, clear, save, copy, exit, fbm, nano")


        while True:
            try:
                command = self.session.prompt(
                    lambda: self.xml_manager.get_prompt(),
                    style=self.style,
                    completer=self.completer
                ).strip()

                if command == "exit":
                    break
                elif command == "cls":
                    clear()
                    self.clear_screen()
                elif command == "clear":
                    self.xml_manager.reset()
                    print("Prompt object cleared. Starting from scratch.")
                elif command.startswith("paste "):
                    self.clipboard_manager.paste_tag(command, self.xml_manager)
                elif command == "nt --str":
                    self.xml_manager.add_project_structure()
                elif command.startswith("nt "):
                    self.xml_manager.create_element(command)
                elif command.startswith("ct "):
                    self.xml_manager.change_tag(command)
                elif command == "ls":
                    self.xml_manager.list_tags()
                elif command == "show":
                    self.xml_manager.show()
                elif command == "prompt":
                    self.xml_manager.go_to_prompt()
                elif command == "save":
                    self.xml_manager.save()
                elif command.startswith("term "):
                    self.xml_manager.add_terminal_output(command[5:])
                elif command == "copy":
                    self.clipboard_manager.copy_content(self.xml_manager)
                elif command == "fbm":
                    self.enter_file_browser_mode()
                elif command == "nano":
                    self.xml_manager.edit_with_nano()
                elif command == "toggle-auto-nav":
                    self.xml_manager.auto_navigate_to_new_tags = not self.xml_manager.auto_navigate_to_new_tags
                    status = "enabled" if self.xml_manager.auto_navigate_to_new_tags else "disabled"
                    print(f"Auto-navigation to new tags {status}")
                else:
                    print("Available commands: nt <tag-name> [\"content\"], paste <tag-name>, ct <tag-name>, ls, show, prompt, cls, clear, save, copy, exit, fbm, nano, toggle-auto-nav")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def enter_file_browser_mode(self):
        # Start designer session
        self.session_manager.start_designer_session(
            xml_manager=self.xml_manager,
            current_path=self.xml_manager.current_path
        )
        
        # Enter file browser mode
        handle_file()
        
        # End designer session
        self.session_manager.end_designer_session()

    def clear_screen(self):
        clear()
        print("🔨 Prompt Designer Mode")
        print("Available commands: nt <tag-name> [\"content\"], paste <tag-name>, ct <tag-name>, ls, show, prompt, cls, clear, save, copy, exit, fbm, nano")
