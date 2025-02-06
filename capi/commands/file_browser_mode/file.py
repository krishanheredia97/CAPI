from .file_manager import FileManager

def handle_file():
    """Handle file selection and content copying."""
    manager = FileManager()
    manager.run()
    return manager.collected_files 