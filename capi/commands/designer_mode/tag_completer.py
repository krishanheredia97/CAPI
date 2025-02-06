from prompt_toolkit.completion import Completer, Completion

class TagCompleter(Completer):
    def __init__(self, get_tags_callback):
        self.get_tags_callback = get_tags_callback

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        if text_before_cursor.startswith("ct "):
            tag_prefix = text_before_cursor[3:].strip()
            tags = self.get_tags_callback()
            for tag in tags:
                if tag.startswith(tag_prefix):
                    yield Completion(tag, start_position=-len(tag_prefix))
        elif text_before_cursor.startswith("nt "):
            if "--".startswith(text_before_cursor[3:].strip()):
                yield Completion("--str", start_position=-len(text_before_cursor[3:].strip()))