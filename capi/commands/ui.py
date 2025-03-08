import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os
import json
import pyperclip
from ..utils.file_utils import (
    get_gitignore_patterns,
    get_file_contents,
    is_binary_file,
    should_ignore
)
from ..utils.structure_utils import generate_directory_structure

class FileTreeView:
    def __init__(self, prompt_dir, include_structure=1):
        self.prompt_dir = os.path.abspath(prompt_dir)
        self.include_structure = include_structure
        self.window = tk.Tk()
        self.window.title("Select Files")
        
        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create checkbox frame
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.pack(fill=tk.X, pady=5)
        
        # Create checkboxes
        self.include_structure_var = tk.BooleanVar(value=True)
        self.include_context_var = tk.BooleanVar(value=True)
        
        structure_cb = ttk.Checkbutton(
            checkbox_frame, 
            text="Include structure",
            variable=self.include_structure_var,
            command=self.update_status
        )
        context_cb = ttk.Checkbutton(
            checkbox_frame, 
            text="Include context",
            variable=self.include_context_var,
            command=self.update_status
        )
        
        structure_cb.pack(side=tk.LEFT, padx=5)
        context_cb.pack(side=tk.LEFT, padx=5)
        
        # Add status label
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=5)
        
        self.update_status()

        # Create search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.after_search_change())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create clear button
        clear_button = ttk.Button(search_frame, text="Clear", command=self.clear_search)
        clear_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Create selection display frame
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create selection label
        selection_label = ttk.Label(selection_frame, text="Selected files:")
        selection_label.pack(anchor=tk.W)
        
        # Create selection text widget
        self.selection_text = tk.Text(selection_frame, height=3, wrap=tk.WORD)
        self.selection_text.pack(fill=tk.X)
        self.selection_text.configure(state='disabled')
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame)
        self.tree.heading('#0', text='Name')
        self.tree.column('#0', width=400)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for selected items
        self.tree.tag_configure('selected', background='lightgreen')
        self.tree.tag_configure('match', background='lightyellow')
        
        # Create button
        copy_button = ttk.Button(main_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.pack(pady=10)
        
        # Add structure status label
        status_text = "Structure will be " + ("included" if self.include_structure else "excluded")
        status_label = ttk.Label(main_frame, text=status_text)
        status_label.pack(pady=5)
        
        # Get ignore patterns
        self.ignore_patterns = get_gitignore_patterns(self.prompt_dir)
        self.always_ignore = ['venv', '__pycache__', '.git', 'node_modules', '.gitignore', 'capi.egg-info']
        
        # Initialize selected items tracking
        self.selected_paths = set()  # Store paths instead of tree items
        self.file_paths = {}  # Store file paths for quick search
        
        # Store all valid files and directories
        self.all_files = []
        self.all_dirs = []
        
        # Bind click event
        self.tree.bind('<ButtonRelease-1>', self.on_click)
        
        # Cache files and populate tree
        self.cache_files()
        self.populate_tree()
        
        # Set window size
        self.window.geometry("450x700")

    def cache_files(self):
        """Cache all valid files and directories"""
        self.all_files = []
        self.all_dirs = []
        for prompt, dirs, files in os.walk(self.prompt_dir):
            rel_prompt = os.path.relpath(prompt, self.prompt_dir)
            
            # Filter directories
            filtered_dirs = []
            for d in dirs:
                dir_path = os.path.join(rel_prompt, d)
                if not should_ignore(dir_path, self.ignore_patterns + self.always_ignore):
                    filtered_dirs.append(d)
                    if dir_path != '.':
                        self.all_dirs.append(dir_path)
            dirs[:] = filtered_dirs
            
            # Filter files
            for f in files:
                file_path = os.path.join(rel_prompt, f)
                full_path = os.path.join(prompt, f)
                if not should_ignore(file_path, self.ignore_patterns + self.always_ignore):
                    if not is_binary_file(full_path):
                        self.all_files.append(file_path)

    def clear_search(self):
        """Clear the search bar and reset the tree view"""
        self.search_var.set('')
        self.populate_tree()

    def after_search_change(self):
        """Handle search input changes with delay to prevent crashes"""
        search_text = self.search_var.get().lower()
        self.filter_tree(search_text)

    def filter_tree(self, search_text):
        """Filter tree items based on search text"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_text:
            self.populate_tree()
            return
        
        # Find matching files and their parent directories
        matched_paths = set()
        
        # Search in cached files
        for file_path in self.all_files:
            if search_text in file_path.lower():
                matched_paths.add(file_path)
                # Add all parent directories
                current_dir = os.path.dirname(file_path)
                while current_dir:
                    matched_paths.add(current_dir)
                    current_dir = os.path.dirname(current_dir)
        
        # Add prompt if we have matches
        if matched_paths:
            prompt_item = self.add_item('', os.path.basename(self.prompt_dir), self.prompt_dir, True)
            self.add_filtered_contents(prompt_item, self.prompt_dir, matched_paths)
            
            # Expand all items
            for item in self.get_all_children(prompt_item):
                self.tree.item(item, open=True)

    def add_filtered_contents(self, parent_item, parent_path, matched_paths):
        """Add filtered directory contents to the tree"""
        try:
            # Add matching directories
            dirs = []
            files = []
            
            for item in sorted(os.listdir(parent_path)):
                item_path = os.path.join(parent_path, item)
                rel_path = os.path.relpath(item_path, self.prompt_dir)
                
                if should_ignore(rel_path, self.ignore_patterns + self.always_ignore):
                    continue
                    
                if os.path.isdir(item_path):
                    if rel_path in matched_paths:
                        dirs.append((item, item_path))
                elif os.path.isfile(item_path) and not is_binary_file(item_path):
                    if rel_path in matched_paths:
                        files.append((item, item_path))
            
            # Add directories first
            for name, dir_path in dirs:
                dir_item = self.add_item(parent_item, name, dir_path, True)
                self.add_filtered_contents(dir_item, dir_path, matched_paths)
            
            # Then add files
            for name, file_path in files:
                file_item = self.add_item(parent_item, name, file_path, False)
                rel_path = os.path.relpath(file_path, self.prompt_dir)
                
                # Apply appropriate tags
                tags = []
                if rel_path in self.selected_paths:
                    tags.append('selected')
                if rel_path in matched_paths:
                    tags.append('match')
                if tags:
                    self.tree.item(file_item, tags=tuple(tags))
                    
        except Exception as e:
            print(f"Error accessing {parent_path}: {e}")

    def add_item(self, parent, text, item_path, is_dir=False):
        """Add an item to the tree"""
        item = self.tree.insert(parent, 'end', text=text, open=True)  # Always open directories
        if not is_dir:
            self.file_paths[item_path] = {'item': item, 'text': text}
        return item

    def get_all_children(self, item):
        """Get all children of an item recursively"""
        children = self.tree.get_children(item)
        result = list(children)
        for child in children:
            result.extend(self.get_all_children(child))
        return result

    def add_directory_contents(self, parent_item, parent_path):
        """Add directory contents to the tree"""
        try:
            items = os.listdir(parent_path)
            
            # Separate directories and files
            dirs = []
            files = []
            for item in items:
                item_path = os.path.join(parent_path, item)
                rel_path = os.path.relpath(item_path, self.prompt_dir)
                
                if should_ignore(rel_path, self.ignore_patterns + self.always_ignore):
                    continue
                    
                if os.path.isdir(item_path):
                    dirs.append(item)
                elif not is_binary_file(item_path):
                    files.append(item)
            
            # Add directories first
            for d in sorted(dirs):
                dir_path = os.path.join(parent_path, d)
                dir_item = self.add_item(parent_item, d, dir_path, True)
                self.add_directory_contents(dir_item, dir_path)
            
            # Then add files
            for f in sorted(files):
                file_path = os.path.join(parent_path, f)
                file_item = self.add_item(parent_item, f, file_path, False)
                # Check if file is selected
                rel_path = os.path.relpath(file_path, self.prompt_dir)
                if rel_path in self.selected_paths:
                    self.tree.item(file_item, tags=('selected',))
                
        except Exception as e:
            print(f"Error accessing {parent_path}: {e}")

    def populate_tree(self):
        """Populate the tree with the directory structure"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add prompt directory
        prompt_name = os.path.basename(self.prompt_dir)
        prompt_item = self.add_item('', prompt_name, self.prompt_dir, True)
        
        self.add_directory_contents(prompt_item, self.prompt_dir)
        
        # Expand all items
        for item in self.get_all_children(prompt_item):
            self.tree.item(item, open=True)

    def on_click(self, event):
        """Handle item clicks"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_remove(self.tree.selection())
            self.toggle_select(item)

    def update_selection_display(self):
        """Update the selection text widget with currently selected files"""
        self.selection_text.configure(state='normal')
        self.selection_text.delete(1.0, tk.END)
        selected_files = sorted(self.selected_paths)
        if selected_files:
            self.selection_text.insert(tk.END, '\n'.join(selected_files))
        self.selection_text.configure(state='disabled')

    def toggle_select(self, item):
        """Toggle selection state of an item"""
        item_path = self.get_item_path(item)
        rel_path = os.path.relpath(item_path, self.prompt_dir)
        
        if os.path.isfile(item_path):
            if rel_path in self.selected_paths:
                self.selected_paths.remove(rel_path)
                self.tree.item(item, tags=())
            else:
                self.selected_paths.add(rel_path)
                self.tree.item(item, tags=('selected',))
        
        self.update_selection_display()

    def select_item(self, item):
        """Select an item and all its children"""
        self.selected_items.add(item)
        self.tree.item(item, tags=('selected',))
        for child in self.get_all_children(item):
            self.selected_items.add(child)
            self.tree.item(child, tags=('selected',))

    def deselect_item(self, item):
        """Deselect an item and all its children"""
        self.selected_items.discard(item)
        self.tree.item(item, tags=())
        for child in self.get_all_children(item):
            self.selected_items.discard(child)
            self.tree.item(child, tags=())

    def get_item_path(self, item):
        """Get the full path for an item"""
        path_parts = []
        while item:
            path_parts.insert(0, self.tree.item(item)['text'])
            item = self.tree.parent(item)
        return os.path.join(self.prompt_dir, *path_parts[1:]) if len(path_parts) > 1 else self.prompt_dir

    def get_selected_files(self):
        """Return list of selected file paths"""
        return sorted(list(self.selected_paths))

    def update_status(self):
        """Update the status label based on checkbox states"""
        status_parts = []
        if self.include_structure_var.get():
            status_parts.append("structure")
        if self.include_context_var.get():
            status_parts.append("context")
            
        status_text = "Including: " + ", ".join(status_parts) if status_parts else "No additional content selected"
        self.status_label.config(text=status_text)

    def copy_to_clipboard(self):
        """Generate and copy output to clipboard"""
        selected_files = self.get_selected_files()
        
        # Generate output
        output = ["<project-context>"]
        
        # Add selected files content
        for file in sorted(selected_files):
            full_path = os.path.join(self.prompt_dir, file)
            content = get_file_contents(full_path)
            if content is not None:
                output.append(f"```{file}\n{content}\n```")
        
        # Add project-context closing tag
        output.append("</project-context>")
        
        # Add structure section if requested
        if self.include_structure_var.get():
            structure = generate_directory_structure(self.prompt_dir, self.ignore_patterns, self.always_ignore)
            # Don't JSON serialize the structure - just add it directly
            output.append(f"\n{structure}")
            
        # Add context if requested
        if self.include_context_var.get():
            ctx_path = Path(self.prompt_dir) / 'prompting' / 'cli' / 'ctx.xml'
            if ctx_path.exists():
                try:
                    with open(ctx_path, 'r', encoding='utf-8') as f:
                        context_content = f.read()
                    output.extend([
                        "\n<context>",
                        context_content,
                        "</context>"
                    ])
                except Exception as e:
                    print(f"Error reading ctx.xml: {e}")
        
        # Copy to clipboard
        final_output = "\n".join(output)
        pyperclip.copy(final_output)
        
        print(f"Project context has been copied to clipboard!")
        print(f"Processed {len(selected_files)} files.")
        if not self.include_structure_var.get():
            print("Project structure was excluded.")
        if not self.include_context_var.get():
            print("Context was excluded.")
        
        self.window.destroy()

        # Save selection for again
        selection_file = os.path.join(self.prompt_dir, 'prompting', 'cli', 'last_selection.json')
        if os.path.exists(os.path.dirname(selection_file)):
            with open(selection_file, 'w') as f:
                json.dump({"files": selected_files}, f)

def open_ui(prompt_dir, include_structure=1):
    """Open the UI selector"""
    if prompt_dir == '.':
        prompt_dir = os.getcwd()
    
    app = FileTreeView(prompt_dir, include_structure)
    app.window.mainloop()