import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import difflib
import os

class DuffyDiffApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DuffyDiff")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # History states for undo function
        self.history = []
        self.current_state = -1
        
        # For difference navigation
        self.diff_blocks = []
        self.current_diff_index = -1
        
        # File paths for saving
        self.left_file_path = None
        self.right_file_path = None
        
        # Flag for scroll synchronization
        self.is_scrolling = False
        
        # Modern colors
        self.colors = {
            "bg": "#FFFFFF",
            "panel_bg": "#F8F9FA",
            "button_bg": "#4285F4",
            "button_hover": "#2B6BC3",
            "button_fg": "white",
            "added": "#E6FFED",
            "added_line": "#CCFFD8",
            "removed": "#FFEBE9",
            "removed_line": "#FFDCE0",
            "unchanged": "white",
            "info": "#5C6BC0",
            "border": "#DEE2E6",
            "header_bg": "#F1F3F4",
            "drop_target_active": "#E3F2FD",
            "undo_button": "#FF5722",
            "nav_button": "#FF9800"
        }
        
        # Configure style
        self.configure_style()
        
        # Create the UI
        self.create_widgets()
        
        # Initialize state
        self.save_state()
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def configure_style(self):
        """Configure the application style"""
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("Header.TFrame", background=self.colors["header_bg"])
        self.style.configure("Panel.TFrame", background=self.colors["panel_bg"])
        
        # Create fonts
        self.default_font = font.nametofont("TkDefaultFont").copy()
        self.default_font.configure(family="Segoe UI", size=10)
        self.root.option_add("*Font", self.default_font)
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header(main_frame)
        
        # Separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill=tk.X, padx=0, pady=0)
        
        # Main container for text panels
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create text panels
        self.create_text_panels(content_frame)
        
        # Footer for statistics
        self.create_footer(main_frame)
        
        # Configure tags for highlighting differences
        self.configure_text_tags()
    
    def create_header(self, parent):
        """Create the header with title and buttons"""
        header_frame = ttk.Frame(parent, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_frame = ttk.Frame(header_frame, style="Header.TFrame")
        title_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Frame for main buttons
        button_frame = ttk.Frame(header_frame, style="Header.TFrame")
        button_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Undo button
        self.undo_btn = tk.Button(button_frame, text="Undo",
                               bg=self.colors["undo_button"], 
                               fg="white",
                               command=self.undo_action,
                               padx=15, pady=7,
                               relief="flat",
                               font=("Segoe UI", 10),
                               state=tk.DISABLED)
        self.undo_btn.pack(side=tk.LEFT, padx=3, pady=3)
        
        # Navigation buttons
        nav_frame = ttk.Frame(button_frame, style="Header.TFrame")
        nav_frame.pack(side=tk.RIGHT, padx=3, pady=3)
        
        self.prev_diff_btn = tk.Button(nav_frame, text="◄ Previous",
                                   bg=self.colors["nav_button"], 
                                   fg="white",
                                   command=self.goto_prev_diff,
                                   padx=10, pady=7,
                                   relief="flat",
                                   font=("Segoe UI", 10),
                                   state=tk.DISABLED)
        self.prev_diff_btn.pack(side=tk.LEFT, padx=3)
        
        self.next_diff_btn = tk.Button(nav_frame, text="Next ►",
                                   bg=self.colors["nav_button"], 
                                   fg="white",
                                   command=self.goto_next_diff,
                                   padx=10, pady=7,
                                   relief="flat",
                                   font=("Segoe UI", 10),
                                   state=tk.DISABLED)
        self.next_diff_btn.pack(side=tk.LEFT, padx=3)
        
        # File loading buttons
        load_left_btn = tk.Button(button_frame, text="Load Left",
                                bg="#FFFFFF", fg="#212529",
                                command=lambda: self.load_file("left"),
                                padx=15, pady=7,
                                relief="flat",
                                font=("Segoe UI", 10))
        load_left_btn.pack(side=tk.LEFT, padx=3, pady=3)
        
        load_right_btn = tk.Button(button_frame, text="Load Right",
                                 bg="#FFFFFF", fg="#212529",
                                 command=lambda: self.load_file("right"),
                                 padx=15, pady=7,
                                 relief="flat",
                                 font=("Segoe UI", 10))
        load_right_btn.pack(side=tk.LEFT, padx=3, pady=3)
        
        # Compare button
        self.compare_btn = tk.Button(button_frame, text="Compare",
                              bg=self.colors["button_bg"], fg="white",
                              command=self.compare_texts,
                              padx=15, pady=7,
                              relief="flat",
                              font=("Segoe UI", 10, "bold"))
        self.compare_btn.pack(side=tk.LEFT, padx=3, pady=3)
        
        # Merge buttons
        merge_left_btn = tk.Button(button_frame, text="Merge All to Left",
                                 bg="#FFFFFF", fg="#212529",
                                 command=lambda: self.merge("left"),
                                 padx=15, pady=7,
                                 relief="flat",
                                 font=("Segoe UI", 10))
        merge_left_btn.pack(side=tk.LEFT, padx=3, pady=3)
        
        merge_right_btn = tk.Button(button_frame, text="Merge All to Right",
                                  bg="#FFFFFF", fg="#212529",
                                  command=lambda: self.merge("right"),
                                  padx=15, pady=7,
                                  relief="flat",
                                  font=("Segoe UI", 10))
        merge_right_btn.pack(side=tk.LEFT, padx=3, pady=3)
        
        save_btn = tk.Button(button_frame, text="Save File",
                           bg="#FFFFFF", fg="#212529",
                           command=self.save_file,
                           padx=15, pady=7,
                           relief="flat",
                           font=("Segoe UI", 10))
        save_btn.pack(side=tk.LEFT, padx=3, pady=3)
    
    def create_text_panels(self, parent):
        """Create the text panels and center controls"""
        # Left panel frame
        self.left_panel = ttk.Frame(parent, style="Panel.TFrame")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_header = ttk.Frame(self.left_panel, style="Panel.TFrame")
        left_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.left_label = ttk.Label(left_header, text="ORIGINAL", 
                             font=("Segoe UI", 11, "bold"),
                             background=self.colors["panel_bg"])
        self.left_label.pack(side=tk.LEFT)
        
        # Left text area with line numbers
        self.left_text_frame = ttk.Frame(self.left_panel)
        self.left_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left line numbers in a canvas for better control
        self.left_line_frame = ttk.Frame(self.left_text_frame, width=40, style="Panel.TFrame")
        self.left_line_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_line_frame.pack_propagate(False)  # Don't shrink
        
        self.left_line_canvas = tk.Canvas(self.left_line_frame, bg='#f0f0f0', 
                                        highlightthickness=0, width=40)
        self.left_line_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create left text widget without scrollbar
        self.left_text = tk.Text(self.left_text_frame, wrap=tk.NONE, 
                               bg=self.colors["bg"],
                               font=("Consolas", 11),
                               borderwidth=1,
                               relief="solid",
                               undo=True)
        self.left_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind text changes to update line numbers
        self.left_text.bind("<<Modified>>", lambda e: self.update_line_numbers(self.left_text, self.left_line_canvas))
        self.left_text.bind("<Configure>", lambda e: self.update_line_numbers(self.left_text, self.left_line_canvas))
        self.left_text.bind("<Key>", lambda e: self.after_idle(lambda: self.update_line_numbers(self.left_text, self.left_line_canvas)))
        
        # Center panel with scrollbar for merge controls
        self.center_panel_container = ttk.Frame(parent, width=180, style="Panel.TFrame")
        self.center_panel_container.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.center_panel_container.pack_propagate(False)  # Don't shrink
        
        # Title for center panel
        center_header = ttk.Frame(self.center_panel_container, style="Panel.TFrame")
        center_header.pack(fill=tk.X, padx=5, pady=5)
        
        center_label = ttk.Label(center_header, text="MERGE", 
                               font=("Segoe UI", 11, "bold"),
                               background=self.colors["panel_bg"])
        center_label.pack(pady=5)
        
        # Create scrollable frame for merge buttons
        self.center_frame = ttk.Frame(self.center_panel_container)
        self.center_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add vertical scrollbar
        self.center_scrollbar = ttk.Scrollbar(self.center_frame)
        self.center_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas with scrollbar
        self.center_canvas = tk.Canvas(self.center_frame, 
                                     bg=self.colors["panel_bg"],
                                     highlightthickness=0,
                                     yscrollcommand=self.center_scrollbar.set)
        self.center_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar to control canvas
        self.center_scrollbar.config(command=self.on_center_scroll)
        
        # Create inner frame for all the merge buttons
        self.center_panel = ttk.Frame(self.center_canvas, style="Panel.TFrame")
        self.center_panel_window = self.center_canvas.create_window((0, 0), window=self.center_panel, anchor="nw")
        
        # Configure canvas resize behavior
        self.center_panel.bind("<Configure>", lambda e: self.center_canvas.configure(scrollregion=self.center_canvas.bbox("all")))
        self.center_canvas.bind("<Configure>", lambda e: self.center_canvas.itemconfig(self.center_panel_window, width=e.width))
        
        # Add mousewheel binding for center panel
        self.center_canvas.bind("<MouseWheel>", self.on_center_mousewheel)
        self.center_frame.bind("<MouseWheel>", self.on_center_mousewheel)
        self.center_panel.bind("<MouseWheel>", self.on_center_mousewheel)
        
        # For Linux
        self.center_canvas.bind("<Button-4>", self.on_linux_mousewheel)
        self.center_canvas.bind("<Button-5>", self.on_linux_mousewheel)
        self.center_frame.bind("<Button-4>", self.on_linux_mousewheel)
        self.center_frame.bind("<Button-5>", self.on_linux_mousewheel)
        self.center_panel.bind("<Button-4>", self.on_linux_mousewheel)
        self.center_panel.bind("<Button-5>", self.on_linux_mousewheel)
        
        # Right panel frame
        self.right_panel = ttk.Frame(parent, style="Panel.TFrame")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_header = ttk.Frame(self.right_panel, style="Panel.TFrame")
        right_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.right_label = ttk.Label(right_header, text="MODIFIED", 
                              font=("Segoe UI", 11, "bold"),
                              background=self.colors["panel_bg"])
        self.right_label.pack(side=tk.LEFT)
        
        # Right text area with line numbers
        self.right_text_frame = ttk.Frame(self.right_panel)
        self.right_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Right line numbers in a canvas for better control
        self.right_line_frame = ttk.Frame(self.right_text_frame, width=40, style="Panel.TFrame")
        self.right_line_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_line_frame.pack_propagate(False)  # Don't shrink
        
        self.right_line_canvas = tk.Canvas(self.right_line_frame, bg='#f0f0f0', 
                                        highlightthickness=0, width=40)
        self.right_line_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create right text widget without scrollbar
        self.right_text = tk.Text(self.right_text_frame, wrap=tk.NONE, 
                                bg=self.colors["bg"],
                                font=("Consolas", 11),
                                borderwidth=1,
                                relief="solid",
                                undo=True)
        self.right_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind text changes to update line numbers
        self.right_text.bind("<<Modified>>", lambda e: self.update_line_numbers(self.right_text, self.right_line_canvas))
        self.right_text.bind("<Configure>", lambda e: self.update_line_numbers(self.right_text, self.right_line_canvas))
        self.left_text.bind("<Key>", lambda e: self.after_idle(lambda: self.update_line_numbers(self.left_text, self.left_line_canvas)))
        
        # Initialize line numbers
        self.update_line_numbers(self.left_text, self.left_line_canvas)
        self.update_line_numbers(self.right_text, self.right_line_canvas)

    def create_footer(self, parent):
        """Create the footer with statistics"""
        footer_frame = ttk.Frame(parent, style="Panel.TFrame", height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.stats_label = ttk.Label(footer_frame, text="Ready for comparison. Use the buttons to load files.", 
                                font=("Segoe UI", 10),
                                background=self.colors["panel_bg"])
        self.stats_label.pack(pady=10)

    def after_idle(self, callback):
        """Execute the callback when the application is idle"""
        self.root.after_idle(callback)

    def configure_text_tags(self):
        """Configure text tags for highlighting"""
        self.left_text.tag_configure("removed", background=self.colors["removed"])
        self.left_text.tag_configure("removed_line", background=self.colors["removed_line"])
        self.left_text.tag_configure("current_diff", background="#FFF9C4")
        
        self.right_text.tag_configure("added", background=self.colors["added"])
        self.right_text.tag_configure("added_line", background=self.colors["added_line"])
        self.right_text.tag_configure("current_diff", background="#FFF9C4")

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts"""
        self.root.bind("<Control-z>", lambda e: self.undo_action())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-o>", lambda e: self.load_file("left"))
        self.root.bind("<Control-p>", lambda e: self.load_file("right"))
        self.root.bind("<Control-d>", lambda e: self.compare_texts())
        self.root.bind("<F5>", lambda e: self.compare_texts())
        
        # Navigation shortcuts
        self.root.bind("<Control-Down>", lambda e: self.goto_next_diff())
        self.root.bind("<Control-Up>", lambda e: self.goto_prev_diff())
        
        # Bind PageUp and PageDown for scrolling
        self.root.bind("<Prior>", lambda e: self.page_scroll(-1))  # PageUp
        self.root.bind("<Next>", lambda e: self.page_scroll(1))    # PageDown

    def page_scroll(self, direction):
        """Handle page up/down scrolling"""
        # Scroll center panel by pages
        if direction < 0:  # Page up
            self.center_canvas.yview_scroll(-1, "pages")
        else:  # Page down
            self.center_canvas.yview_scroll(1, "pages")
        
        # Sync text panels
        self.sync_text_panels_with_center()

    def update_line_numbers(self, text_widget, line_canvas):
        """Update line numbers in the line canvas"""
        # Get first visible line and last visible line
        first_line = int(float(text_widget.index("@0,0").split('.')[0]))
        last_line = int(float(text_widget.index("@0,%d" % text_widget.winfo_height()).split('.')[0]))
        
        # Clear canvas
        line_canvas.delete("all")
        
        # Create line numbers
        for i in range(max(1, first_line-1), last_line+2):
            # Calculate y position
            y_pos = text_widget.dlineinfo(f"{i}.0")
            if y_pos:  # Line is visible
                line_canvas.create_text(
                    20,  # x position
                    y_pos[1],  # y position
                    text=str(i),
                    anchor="center",
                    fill="#606060",
                    font=("Consolas", 10)
                )
        
        # Reset modified flag
        text_widget.edit_modified(False)

    def on_center_scroll(self, *args):
        """Handle scrolling in center panel and sync with text panels"""
        # Update center panel scroll position
        self.center_canvas.yview(*args)
        
        if not self.is_scrolling:
            self.is_scrolling = True
            # Sync text panels with center panel's scroll position
            self.sync_text_panels_with_center()
            self.is_scrolling = False

    def on_center_mousewheel(self, event):
        """Handle mousewheel scrolling in center panel and sync with text panels"""
        if self.is_scrolling:
            return "break"
            
        self.is_scrolling = True
        
        # Get mouse wheel movement
        if hasattr(event, 'delta'):
            delta = -1 * (event.delta // 120)
        else:
            # For platforms where event.delta is not available
            if event.num == 4:
                delta = -1
            else:
                delta = 1
        
        # Scroll center panel
        self.center_canvas.yview_scroll(delta, "units")
        
        # Sync text panels with center panel's scroll position
        self.sync_text_panels_with_center()
        
        self.is_scrolling = False
        return "break"  # Prevent default scrolling

    def on_linux_mousewheel(self, event):
        """Handle mousewheel scrolling in center panel on Linux"""
        if self.is_scrolling:
            return "break"
            
        self.is_scrolling = True
        
        if event.num == 4:
            delta = -1
        else:
            delta = 1
            
        # Scroll center panel
        self.center_canvas.yview_scroll(delta, "units")
        
        # Sync text panels
        self.sync_text_panels_with_center()
        
        self.is_scrolling = False
        return "break"  # Prevent default scrolling

    def sync_text_panels_with_center(self):
        """Sync text panels with center panel scroll position"""
        # If there are no differences, nothing to sync
        if not self.diff_blocks:
            return
        
        # Get current center panel scroll position
        center_pos = self.center_canvas.yview()
        
        # Calculate which difference block is most visible
        visible_center = center_pos[0] + ((center_pos[1] - center_pos[0]) / 2)
        total_blocks = len(self.diff_blocks)
        
        # Find the diff block closest to the center of the visible area
        target_idx = int(visible_center * total_blocks)
        if target_idx >= total_blocks:
            target_idx = total_blocks - 1
        
        # Navigate to that difference without updating center scroll
        self.goto_diff(target_idx, update_center=False)

    def goto_next_diff(self):
        """Navigate to the next difference"""
        if not self.diff_blocks:
            return
            
        if self.current_diff_index < len(self.diff_blocks) - 1:
            self.current_diff_index += 1
            self.goto_diff(self.current_diff_index)

    def goto_prev_diff(self):
        """Navigate to the previous difference"""
        if not self.diff_blocks:
            return
            
        if self.current_diff_index > 0:
            self.current_diff_index -= 1
            self.goto_diff(self.current_diff_index)

    def goto_diff(self, diff_idx, update_center=True):
        """Navigate to a specific difference"""
        if not self.diff_blocks or diff_idx < 0 or diff_idx >= len(self.diff_blocks):
            return
            
        # Remove current highlight if any
        self.clear_current_diff_highlight()
        
        # Set current difference index
        self.current_diff_index = diff_idx
        
        # Get current difference
        curr_diff = self.diff_blocks[self.current_diff_index]
            
        # Highlight the difference
        self.highlight_current_diff()
        
        # Scroll text panels to make the difference visible
        left_start = curr_diff["left_start"]
        right_start = curr_diff["right_start"]
        
        self.left_text.see(left_start)
        self.right_text.see(right_start)
        
        # Update line numbers after scrolling
        self.update_line_numbers(self.left_text, self.left_line_canvas)
        self.update_line_numbers(self.right_text, self.right_line_canvas)
        
        # Update center panel scroll position if requested
        if update_center:
            # Calculate position in center panel
            pos = self.current_diff_index / max(1, len(self.diff_blocks) - 1)
            self.center_canvas.yview_moveto(pos)
        
        # Update status
        self.stats_label.config(text=f"Viewing difference {self.current_diff_index + 1} of {len(self.diff_blocks)}")

    def clear_current_diff_highlight(self):
        """Clear the current difference highlight"""
        self.left_text.tag_remove("current_diff", "1.0", tk.END)
        self.right_text.tag_remove("current_diff", "1.0", tk.END)

    def highlight_current_diff(self):
        """Highlight the current difference"""
        if not self.diff_blocks or self.current_diff_index < 0:
            return
            
        curr_diff = self.diff_blocks[self.current_diff_index]
        
        # Apply highlighting
        left_start = curr_diff["left_start"]
        left_end = curr_diff["left_end"]
        right_start = curr_diff["right_start"]
        right_end = curr_diff["right_end"]
        
        # Apply special highlighting to current difference
        if float(left_end) > float(left_start):
            self.left_text.tag_add("current_diff", left_start, left_end)
            
        if float(right_end) > float(right_start):
            self.right_text.tag_add("current_diff", right_start, right_end)

    def load_file(self, side):
        """Load a file to the specified panel"""
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not filepath:
                return
                
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                    
            if side == "left":
                self.left_text.delete(1.0, tk.END)
                self.left_text.insert(tk.END, content)
                self.left_file_path = filepath
                self.left_label.config(text=f"ORIGINAL: {os.path.basename(filepath)}")
                self.stats_label.config(text=f"File loaded on left: {os.path.basename(filepath)}")
            else:
                self.right_text.delete(1.0, tk.END)
                self.right_text.insert(tk.END, content)
                self.right_file_path = filepath
                self.right_label.config(text=f"MODIFIED: {os.path.basename(filepath)}")
                self.stats_label.config(text=f"File loaded on right: {os.path.basename(filepath)}")
            
            # Update line numbers
            self.update_line_numbers(self.left_text, self.left_line_canvas)
            self.update_line_numbers(self.right_text, self.right_line_canvas)
            
            # Save state AFTER loading file
            self.save_state()
            
            # Check if both panels have content for auto-comparison
            left_content = self.left_text.get("1.0", tk.END).strip()
            right_content = self.right_text.get("1.0", tk.END).strip()
            
            if left_content and right_content:
                # Only auto-compare after loading files (not during editing)
                self.compare_texts()
                
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load file: {str(e)}")

    def save_file(self):
        """Save the active text panel to a file"""
        active_text = self.root.focus_get()
        
        if active_text == self.left_text:
            initial_file = self.left_file_path
            content = self.left_text.get(1.0, tk.END)
            panel = "left"
        elif active_text == self.right_text:
            initial_file = self.right_file_path
            content = self.right_text.get(1.0, tk.END)
            panel = "right"
        else:
            messagebox.showwarning("Warning", "Select a text editor panel first (left or right)")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=os.path.basename(initial_file) if initial_file else None
        )
        
        if not filepath:
            return
            
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            
            # Update file path
            if panel == "left":
                self.left_file_path = filepath
                self.left_label.config(text=f"ORIGINAL: {os.path.basename(filepath)}")
            else:
                self.right_file_path = filepath
                self.right_label.config(text=f"MODIFIED: {os.path.basename(filepath)}")
                
            messagebox.showinfo("Success", f"File saved as {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unable to save file: {str(e)}")

    def save_state(self):
        """Save current state to history"""
        # Get current content
        left_content = self.left_text.get(1.0, tk.END)
        right_content = self.right_text.get(1.0, tk.END)
        
        # Skip if content is empty or unchanged
        if (self.current_state >= 0 and 
            self.history[self.current_state]["left"] == left_content and 
            self.history[self.current_state]["right"] == right_content):
            return
        
        # If we're in the middle of history, cut off future states
        if self.current_state < len(self.history) - 1:
            self.history = self.history[:self.current_state + 1]
        
        # Add new state to history
        self.history.append({
            "left": left_content,
            "right": right_content
        })
        
        # Update current state index
        self.current_state = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > 20:
            self.history = self.history[-20:]
            self.current_state = len(self.history) - 1
        
        # Enable undo button if we have states to undo to
        if self.current_state > 0:
            self.undo_btn.config(state=tk.NORMAL)

    def undo_action(self):
        """Undo last action by restoring previous state"""
        # Check if undo is possible
        if self.current_state <= 0 or len(self.history) <= 1:
            messagebox.showinfo("Information", "No action to undo")
            self.undo_btn.config(state=tk.DISABLED)
            return
        
        # Move to previous state
        self.current_state -= 1
        state = self.history[self.current_state]
        
        # Restore panel content
        self.left_text.delete(1.0, tk.END)
        self.left_text.insert(1.0, state["left"])
        
        self.right_text.delete(1.0, tk.END)
        self.right_text.insert(1.0, state["right"])
        
        # Update line numbers
        self.update_line_numbers(self.left_text, self.left_line_canvas)
        self.update_line_numbers(self.right_text, self.right_line_canvas)
        
        # Update interface
        self.stats_label.config(text=f"Action undone (step {self.current_state+1}/{len(self.history)})")
        
        # If we've gone back to first state, disable the button
        if self.current_state <= 0:
            self.undo_btn.config(state=tk.DISABLED)
        
        # Automatically run compare after undo
        self.compare_texts()

    def apply_highlights(self):
        """Apply highlighting to the text without replacing content"""
        # Clear all tags first
        self.left_text.tag_remove("removed_line", "1.0", tk.END)
        self.right_text.tag_remove("added_line", "1.0", tk.END)
        self.clear_current_diff_highlight()
        
        # Apply highlighting for all differences
        for diff in self.diff_blocks:
            left_start = diff["left_start"]
            left_end = diff["left_end"]
            right_start = diff["right_start"]
            right_end = diff["right_end"]
            
            # Apply regular difference highlighting
            if float(left_end) > float(left_start):
                self.left_text.tag_add("removed_line", left_start, left_end)
            if float(right_end) > float(right_start):
                self.right_text.tag_add("added_line", right_start, right_end)

    def compare_texts(self):
        """Perform text comparison"""
        # Clear any previous merge controls
        for widget in self.center_panel.winfo_children():
            widget.destroy()
        
        # Reset diff navigation
        self.diff_blocks = []
        self.current_diff_index = -1
        
        # Get the current content
        left_content = self.left_text.get(1.0, tk.END).splitlines()
        right_content = self.right_text.get(1.0, tk.END).splitlines()
        
        # Check if there's content to compare
        if not left_content or not right_content:
            self.stats_label.config(text="Enter text in both panels")
            self.prev_diff_btn.config(state=tk.DISABLED)
            self.next_diff_btn.config(state=tk.DISABLED)
            return
        
        # Use SequenceMatcher for block-level differences
        matcher = difflib.SequenceMatcher(None, left_content, right_content)
        
        added = 0
        removed = 0
        
        # Track line indices in both panels
        left_line_idx = 1
        right_line_idx = 1
        
        # Process difference blocks
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            left_block_lines = i2 - i1
            right_block_lines = j2 - j1
            
            if tag == 'equal':
                # Equal block, just track line indices
                left_line_idx += left_block_lines
                right_line_idx += right_block_lines
                    
            else:  # 'replace', 'delete', 'insert'
                # Store positions for highlighting
                if left_block_lines > 0:
                    start_left = f"{left_line_idx}.0"
                    end_left = f"{left_line_idx + left_block_lines}.0"
                    removed += left_block_lines
                else:
                    start_left = f"{left_line_idx}.0"
                    end_left = start_left
                
                if right_block_lines > 0:
                    start_right = f"{right_line_idx}.0"
                    end_right = f"{right_line_idx + right_block_lines}.0"
                    added += right_block_lines
                else:
                    start_right = f"{right_line_idx}.0"
                    end_right = start_right
                
                # Current diff index for this block
                diff_idx = len(self.diff_blocks)
                
                # Add merge buttons for this block
                if left_block_lines > 0 or right_block_lines > 0:
                    # Create a distinct frame for each difference
                    merge_frame = ttk.Frame(self.center_panel, style="Panel.TFrame")
                    merge_frame.pack(pady=5, fill=tk.X, padx=3)
                    
                    # Add a border to make the frame stand out
                    border_frame = ttk.Frame(merge_frame, style="Panel.TFrame", relief="solid", borderwidth=1)
                    border_frame.pack(fill=tk.X, expand=True)
                    
                    # Inner frame for content
                    inner_frame = ttk.Frame(border_frame, style="Panel.TFrame", padding=5)
                    inner_frame.pack(fill=tk.X, expand=True)
                    
                    # Add difference number indicator as a clickable button
                    diff_btn = tk.Button(
                        inner_frame,
                        text=f"Diff #{diff_idx + 1}",
                        bg=self.colors["button_bg"],
                        fg="white",
                        font=("Segoe UI", 9, "bold"),
                        relief="flat",
                        padx=5, pady=5,
                        command=lambda idx=diff_idx: self.goto_diff(idx)
                    )
                    diff_btn.pack(pady=2, fill=tk.X)
                    
                    # Show type of difference with better visual
                    if tag == 'replace':
                        diff_type = "Modified"
                        type_color = "#E8EAF6"  # Light indigo
                    elif tag == 'delete':
                        diff_type = "Deleted"
                        type_color = "#FFEBEE"  # Light red
                    else:  # 'insert'
                        diff_type = "Added"
                        type_color = "#E0F2F1"  # Light teal
                    
                    # Show line numbers affected
                    left_lines_text = f"Lines: {left_line_idx}"
                    if left_block_lines > 1:
                        left_lines_text += f"-{left_line_idx + left_block_lines - 1}"
                        
                    right_lines_text = f"Lines: {right_line_idx}"
                    if right_block_lines > 1:
                        right_lines_text += f"-{right_line_idx + right_block_lines - 1}"
                    
                    # Create a frame for the diff type with background color
                    type_frame = ttk.Frame(inner_frame, style="Panel.TFrame")
                    type_frame.pack(fill=tk.X, pady=2)
                    
                    type_label = ttk.Label(
                        type_frame,
                        text=f"Type: {diff_type}",
                        background=type_color,
                        font=("Segoe UI", 8, "bold"),
                        padding=3
                    )
                    type_label.pack(fill=tk.X)
                    
                    # Display line information
                    if left_block_lines > 0:
                        left_info = ttk.Label(
                            inner_frame,
                            text=f"Left: {left_lines_text}",
                            background=self.colors["panel_bg"],
                            font=("Segoe UI", 8)
                        )
                        left_info.pack(fill=tk.X, pady=1)
                    
                    if right_block_lines > 0:
                        right_info = ttk.Label(
                            inner_frame,
                            text=f"Right: {right_lines_text}",
                            background=self.colors["panel_bg"],
                            font=("Segoe UI", 8)
                        )
                        right_info.pack(fill=tk.X, pady=1)
                    
                    # Button to copy from left to right
                    if left_block_lines > 0:
                        copy_right_btn = tk.Button(
                            inner_frame, 
                            text="Copy →",
                            bg="#E3F2FD", 
                            fg="#0D47A1",
                            width=10, 
                            height=1,
                            relief="raised",
                            borderwidth=2,
                            font=("Segoe UI", 10, "bold"),
                            command=lambda sl=start_left, el=end_left, sr=start_right, er=end_right: 
                                    self.merge_selection(sl, el, sr, er, "right")
                        )
                        copy_right_btn.pack(pady=2, fill=tk.X)
                    
                    # Button to copy from right to left
                    if right_block_lines > 0:
                        copy_left_btn = tk.Button(
                            inner_frame, 
                            text="← Copy",
                            bg="#E8F5E9", 
                            fg="#1B5E20",
                            width=10, 
                            height=1,
                            relief="raised",
                            borderwidth=2,
                            font=("Segoe UI", 10, "bold"),
                            command=lambda sl=start_left, el=end_left, sr=start_right, er=end_right: 
                                    self.merge_selection(sl, el, sr, er, "left")
                        )
                        copy_left_btn.pack(pady=2, fill=tk.X)
                    
                    # Save this block for future reference
                    self.diff_blocks.append({
                        "left_start": start_left,
                        "left_end": end_left,
                        "right_start": start_right,
                        "right_end": end_right,
                        "left_lines": left_block_lines,
                        "right_lines": right_block_lines,
                        "tag": tag,
                        "left_line_idx": left_line_idx,
                        "right_line_idx": right_line_idx
                    })
                
                # Update line indices
                left_line_idx += left_block_lines
                right_line_idx += right_block_lines
        
        # Apply highlighting to the text
        self.apply_highlights()
        
        # Update statistics
        total_changes = len(self.diff_blocks)
        if total_changes > 0:
            self.stats_label.config(text=f"Differences found: {total_changes} blocks (Added: {added}, Removed: {removed} lines)")
            
            # Enable navigation buttons
            self.prev_diff_btn.config(state=tk.NORMAL)
            self.next_diff_btn.config(state=tk.NORMAL)
            
            # Initialize difference navigation
            self.current_diff_index = 0
            self.highlight_current_diff()
            
            # Jump to first difference
            self.goto_diff(0)
        else:
            self.stats_label.config(text="No differences found. Files are identical.")
            self.prev_diff_btn.config(state=tk.DISABLED)
            self.next_diff_btn.config(state=tk.DISABLED)
        
        # Make sure the center panel is properly scrollable
        self.center_canvas.configure(scrollregion=self.center_canvas.bbox("all"))
        
        # Update line numbers
        self.update_line_numbers(self.left_text, self.left_line_canvas)
        self.update_line_numbers(self.right_text, self.right_line_canvas)

    def merge_selection(self, left_start, left_end, right_start, right_end, direction):
        """Merge selections between panels"""
        try:
            # Save state before merge
            self.save_state()
            
            if direction == "right":
                # Get content from left panel
                content = self.left_text.get(left_start, left_end)
                
                # Clear content at destination
                self.right_text.delete(right_start, right_end)
                
                # Insert content at destination
                self.right_text.insert(right_start, content)
                
            else:  # direction == "left"
                # Get content from right panel
                content = self.right_text.get(right_start, right_end)
                
                # Clear content at destination
                self.left_text.delete(left_start, left_end)
                
                # Insert content at destination
                self.left_text.insert(left_start, content)
            
            # Update line numbers
            self.update_line_numbers(self.left_text, self.left_line_canvas)
            self.update_line_numbers(self.right_text, self.right_line_canvas)
            
            # Save state after merge
            self.save_state()
            
            # Run comparison again to update the view
            self.compare_texts()
            
        except Exception as e:
            messagebox.showerror("Merge Error", f"Error during merge: {str(e)}")

    def merge(self, direction):
        """Perform complete merge in one direction"""
        # Confirm with user
        if direction == "left":
            msg = "This will replace all content in the left panel with content from the right panel. Continue?"
        else:
            msg = "This will replace all content in the right panel with content from the left panel. Continue?"
            
        confirm = messagebox.askyesno("Confirm Merge", msg)
        if not confirm:
            return
        
        # Save state before merge
        self.save_state()
        
        if direction == "left":
            # Copy text from right to left
            content = self.right_text.get(1.0, tk.END)
            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(tk.END, content)
        else:
            # Copy text from left to right
            content = self.left_text.get(1.0, tk.END)
            self.right_text.delete(1.0, tk.END)
            self.right_text.insert(tk.END, content)
        
        # Update line numbers
        self.update_line_numbers(self.left_text, self.left_line_canvas)
        self.update_line_numbers(self.right_text, self.right_line_canvas)
        
        # Save state after merge
        self.save_state()
        
        messagebox.showinfo("Operation Complete", f"Merged to {'left' if direction == 'left' else 'right'} completed")
        
        # Recalculate differences
        self.compare_texts()


def main():
    # Initialize application with improved error handling
    try:
        root = tk.Tk()
        root.title("DuffyDiff")
        
        # Set application icon if available
        try:
            root.iconbitmap("duffy.ico")
        except:
            pass  # Icon not found, use default
            
        app = DuffyDiffApp(root)
        
        # Set minimum window size
        root.minsize(1000, 600)
        
        # Center window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 1400
        window_height = 800
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Startup Error", f"Error starting application: {str(e)}")


if __name__ == "__main__":
    main()