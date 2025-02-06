from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from .file_completer import FileCompleter
import pyperclip
from ...utils.file_utils import get_file_contents
from ..session_manager import SessionManager

class FileManager:
    def __init__(self):
        self.completer = FileCompleter()
        self.collected_files = []  # Store tuples of (file_path, content)
        self.session_manager = SessionManager()

    def format_output(self) -> str:
        if not self.collected_files:
            return ""
        
        formatted_files = []
        for file_path, content in self.collected_files:
            formatted_files.append(f"```{file_path}\n{content}\n```")
            
        return '\n'.join(formatted_files)

    def run(self):
        is_designer_mode = self.session_manager.is_designer_session_active()
        
        print("📁 File Browser Mode")
        if is_designer_mode:
            print("🟣 Prompt Designer Session Active - type 'paste' when you're done")
        print("Commands: file <filename>, copy, paste" if is_designer_mode else "Commands: file <filename>, copy")
        print("Type part of a filename to search, use TAB to complete")
        
        session = PromptSession(
            HTML("<ansiyellow>browser></ansiyellow> "),
            completer=self.completer,
            complete_while_typing=True
        )

        try:
            while True:
                result = session.prompt().strip()
                
                if result == '<':
                    break
                    
                if result == 'paste' and is_designer_mode:
                    if self.collected_files:
                        final_content = self.format_output()
                        designer_context = self.session_manager.designer_context
                        designer_context.xml_manager.create_element(f'nt project-files "{final_content}"')
                        print("Files added to prompt designer session")
                        break
                    else:
                        print("No content collected yet")
                    continue
                    
                if result == 'copy':
                    if self.collected_files:
                        final_content = self.format_output()
                        pyperclip.copy(final_content)
                        print("All collected content copied to clipboard!")
                        if not is_designer_mode:
                            break
                    else:
                        print("No content collected yet")
                    continue

                if not result.startswith('file '):
                    print("Use 'file <filename>' to add content")
                    continue

                file_path = result[5:].strip()
                content = get_file_contents(file_path)
                
                if content:
                    self.collected_files.append((file_path, content))
                    print(f"Content of {file_path} added to collection!")
                else:
                    print(f"Error: Could not read file {file_path}")

        except (KeyboardInterrupt, EOFError):
            return