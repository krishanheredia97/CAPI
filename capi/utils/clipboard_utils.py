import pyperclip

def get_clipboard_content():
    """Get content from clipboard."""
    try:
        return pyperclip.paste()
    except Exception as e:
        raise Exception(f"Failed to get clipboard content: {str(e)}")
