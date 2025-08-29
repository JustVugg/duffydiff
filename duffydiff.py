import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import difflib
import os
from datetime import datetime

class ModernDiffApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DiffTool - File Compare")
        self.root.geometry("1400x800")
        
        # Settings
        self.auto_compare = True
        self.compare_delay = 500
        self.compare_timer = None
        self.sync_scroll = True
        self.is_syncing = False
        
        # Files
        self.left_file = None
        self.right_file = None
        
        # Differences
        self.differences = []
        self.current_diff = -1
        self.diff_widgets = []
        
        # History for undo
        self.history = []
        self.history_index = -1
        
        # Create UI
        self.create_toolbar()
        self.create_main_panels()
        self.create_statusbar()
        self.setup_bindings()
        
    def create_toolbar(self):
        """Create modern toolbar"""
        toolbar = tk.Frame(self.root, bg="#1e272e", height=45)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Style for toolbar buttons
        button_style = {
            'font': ('Segoe UI', 10),
            'bd': 0,
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2'
        }
        
        # File buttons
        btn = tk.Button(toolbar, text="📁 Open Left", command=lambda: self.load_file("left"),
                       bg="#0984e3", fg="white", activebackground="#74b9ff", **button_style)
        btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(btn, "#0984e3", "#74b9ff")
        
        btn = tk.Button(toolbar, text="📁 Open Right", command=lambda: self.load_file("right"),
                       bg="#0984e3", fg="white", activebackground="#74b9ff", **button_style)
        btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(btn, "#0984e3", "#74b9ff")
        
        # Separator
        tk.Frame(toolbar, width=2, bg="#2d3436").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Compare buttons
        btn = tk.Button(toolbar, text="🔍 Compare", command=self.compare,
                       bg="#00b894", fg="white", activebackground="#55efc4", **button_style)
        btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(btn, "#00b894", "#55efc4")
        
        self.auto_btn = tk.Button(toolbar, text=f"⚡ Auto: {'ON' if self.auto_compare else 'OFF'}", 
                                 command=self.toggle_auto_compare,
                                 bg="#00b894" if self.auto_compare else "#636e72", 
                                 fg="white", activebackground="#55efc4", **button_style)
        self.auto_btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(self.auto_btn, "#00b894" if self.auto_compare else "#636e72", "#55efc4")
        
        # Separator
        tk.Frame(toolbar, width=2, bg="#2d3436").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Navigation buttons
        btn = tk.Button(toolbar, text="◀ Previous", command=self.prev_diff,
                       bg="#fdcb6e", fg="#2d3436", activebackground="#ffeaa7", **button_style)
        btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(btn, "#fdcb6e", "#ffeaa7")
        
        btn = tk.Button(toolbar, text="Next ▶", command=self.next_diff,
                       bg="#fdcb6e", fg="#2d3436", activebackground="#ffeaa7", **button_style)
        btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(btn, "#fdcb6e", "#ffeaa7")
        
        # Separator
        tk.Frame(toolbar, width=2, bg="#2d3436").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Undo button
        btn = tk.Button(toolbar, text="↩ Undo", command=self.undo,
                       bg="#a29bfe", fg="white", activebackground="#d6a2ff", **button_style)
        btn.pack(side=tk.LEFT, padx=3, pady=7)
        self.add_hover_effect(btn, "#a29bfe", "#d6a2ff")
        
        # Info label
        self.info_label = tk.Label(toolbar, text="Ready", bg="#1e272e", fg="white", 
                                  font=("Segoe UI", 11, "bold"))
        self.info_label.pack(side=tk.RIGHT, padx=20)
        
    def add_hover_effect(self, button, normal_color, hover_color):
        """Add hover effect to button"""
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=normal_color))
        
    def create_main_panels(self):
        """Create the main comparison panels"""
        main_frame = tk.Frame(self.root, bg="#dfe6e9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # LEFT PANEL
        left_frame = tk.Frame(main_frame, bg="#b2bec3")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Left title
        title_frame = tk.Frame(left_frame, bg="#2d3436", height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        self.left_title = tk.Label(title_frame, text="Left: No file", bg="#2d3436", fg="white", 
                                  font=("Segoe UI", 11), pady=5)
        self.left_title.pack(expand=True)
        
        # Left text frame (contains line numbers + text)
        left_text_frame = tk.Frame(left_frame)
        left_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Text widget for text
        self.left_text = tk.Text(left_text_frame, wrap=tk.NONE, font=("Consolas", 12),
                                bg="#ffffff", fg="#2d3436", bd=0, padx=10, pady=5, 
                                undo=True, insertbackground="#2d3436")
        
        # Create scrollbars
        self.left_vscroll = ttk.Scrollbar(left_text_frame, orient=tk.VERTICAL)
        left_hscroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL)
        
        # Pack in correct order
        self.left_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        left_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Line numbers canvas
        self.left_lines = tk.Canvas(left_text_frame, width=60, bg="#ecf0f1", bd=0, highlightthickness=0)
        self.left_lines.pack(side=tk.LEFT, fill=tk.Y)
        
        # Configure scrolling
        self.left_text.config(yscrollcommand=self.sync_left_scroll)
        self.left_text.config(xscrollcommand=left_hscroll.set)
        self.left_vscroll.config(command=self.sync_left_view)
        left_hscroll.config(command=self.left_text.xview)
        
        # MIDDLE PANEL
        middle_frame = tk.Frame(main_frame, width=160, bg="#b2bec3")
        middle_frame.grid(row=0, column=1, sticky="ns", padx=2, pady=2)
        middle_frame.grid_propagate(False)
        
        # Middle title
        title_frame = tk.Frame(middle_frame, bg="#2d3436", height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Actions", bg="#2d3436", fg="white", 
                font=("Segoe UI", 11), pady=5).pack(expand=True)
        
        # Middle canvas (no scrollbar - it follows text panels)
        self.middle_canvas = tk.Canvas(middle_frame, bg="#dfe6e9", bd=0, highlightthickness=0)
        self.middle_canvas.pack(fill=tk.BOTH, expand=True)
        
        # RIGHT PANEL
        right_frame = tk.Frame(main_frame, bg="#b2bec3")
        right_frame.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        
        # Right title
        title_frame = tk.Frame(right_frame, bg="#2d3436", height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        self.right_title = tk.Label(title_frame, text="Right: No file", bg="#2d3436", fg="white", 
                                   font=("Segoe UI", 11), pady=5)
        self.right_title.pack(expand=True)
        
        # Right text frame (contains line numbers + text)
        right_text_frame = tk.Frame(right_frame)
        right_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Text widget for text
        self.right_text = tk.Text(right_text_frame, wrap=tk.NONE, font=("Consolas", 12),
                                 bg="#ffffff", fg="#2d3436", bd=0, padx=10, pady=5, 
                                 undo=True, insertbackground="#2d3436")
        
        # Create scrollbars
        self.right_vscroll = ttk.Scrollbar(right_text_frame, orient=tk.VERTICAL)
        right_hscroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL)
        
        # Pack in correct order
        self.right_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Line numbers canvas
        self.right_lines = tk.Canvas(right_text_frame, width=60, bg="#ecf0f1", bd=0, highlightthickness=0)
        self.right_lines.pack(side=tk.LEFT, fill=tk.Y)
        
        # Configure scrolling
        self.right_text.config(yscrollcommand=self.sync_right_scroll)
        self.right_text.config(xscrollcommand=right_hscroll.set)
        self.right_vscroll.config(command=self.sync_right_view)
        right_hscroll.config(command=self.right_text.xview)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Configure tags
        self.configure_tags()
        
        # Bind text changes
        self.left_text.bind("<KeyRelease>", lambda e: self.on_text_change())
        self.right_text.bind("<KeyRelease>", lambda e: self.on_text_change())
        
    def sync_left_scroll(self, first, last):
        """Sync left scroll with others"""
        self.left_vscroll.set(first, last)
        if self.sync_scroll and not self.is_syncing:
            self.is_syncing = True
            self.right_text.yview_moveto(first)
            self.is_syncing = False
        self.update_line_numbers()
        self.update_middle_panel()
        
    def sync_right_scroll(self, first, last):
        """Sync right scroll with others"""
        self.right_vscroll.set(first, last)
        if self.sync_scroll and not self.is_syncing:
            self.is_syncing = True
            self.left_text.yview_moveto(first)
            self.is_syncing = False
        self.update_line_numbers()
        self.update_middle_panel()
        
    def sync_left_view(self, *args):
        """Sync left view command"""
        self.left_text.yview(*args)
        if self.sync_scroll and not self.is_syncing:
            self.is_syncing = True
            self.right_text.yview(*args)
            self.is_syncing = False
        self.update_line_numbers()
        self.update_middle_panel()
        
    def sync_right_view(self, *args):
        """Sync right view command"""
        self.right_text.yview(*args)
        if self.sync_scroll and not self.is_syncing:
            self.is_syncing = True
            self.left_text.yview(*args)
            self.is_syncing = False
        self.update_line_numbers()
        self.update_middle_panel()
        
    def configure_tags(self):
        """Configure text tags for highlighting"""
        # Light colors for better visibility
        self.left_text.tag_configure("added", background="#a8e6cf")
        self.left_text.tag_configure("removed", background="#ffd3b6")
        self.left_text.tag_configure("modified", background="#ffaaa5")
        self.left_text.tag_configure("current", background="#fff200", borderwidth=2, relief="solid")
        
        self.right_text.tag_configure("added", background="#a8e6cf")
        self.right_text.tag_configure("removed", background="#ffd3b6")
        self.right_text.tag_configure("modified", background="#ffaaa5")
        self.right_text.tag_configure("current", background="#fff200", borderwidth=2, relief="solid")
        
    def create_statusbar(self):
        """Create status bar"""
        self.statusbar = tk.Frame(self.root, bg="#2d3436", height=30)
        self.statusbar.pack(fill=tk.X)
        self.statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(self.statusbar, text="Ready", bg="#2d3436", fg="white", 
                                    font=("Segoe UI", 10))
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        # Add timestamp label
        self.time_label = tk.Label(self.statusbar, text="", bg="#2d3436", fg="#b2bec3", 
                                  font=("Segoe UI", 9))
        self.time_label.pack(side=tk.RIGHT, padx=15, pady=5)
        
    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-o>", lambda e: self.load_file("left"))
        self.root.bind("<Control-O>", lambda e: self.load_file("right"))
        self.root.bind("<F5>", lambda e: self.compare())
        self.root.bind("<F3>", lambda e: self.next_diff())
        self.root.bind("<Shift-F3>", lambda e: self.prev_diff())
        self.root.bind("<Control-z>", lambda e: self.undo())
        
    def update_line_numbers(self):
        """Update line numbers for both panels"""
        self.update_single_line_numbers(self.left_text, self.left_lines)
        self.update_single_line_numbers(self.right_text, self.right_lines)
        
    def update_single_line_numbers(self, text_widget, canvas):
        """Update line numbers on canvas"""
        canvas.delete("all")
        
        # Get the first visible line
        first_visible = text_widget.index("@0,0")
        first_line_num = int(first_visible.split('.')[0])
        
        # Get the last visible line
        last_visible = text_widget.index(f"@0,{text_widget.winfo_height()}")
        last_line_num = int(last_visible.split('.')[0])
        
        # Draw line numbers
        for line_num in range(first_line_num, last_line_num + 1):
            # Get y position of line
            bbox = text_widget.bbox(f"{line_num}.0")
            if bbox:
                y = bbox[1] + bbox[3] // 2
                canvas.create_text(50, y, text=str(line_num), anchor="e", 
                                 font=("Consolas", 11), fill="#636e72")
                
    def update_middle_panel(self):
        """Update middle panel to show differences at correct positions"""
        self.middle_canvas.delete("all")
        
        if not self.differences:
            return
            
        # Get the first visible line to calculate relative positions
        first_visible = self.left_text.index("@0,0")
        first_line_num = int(first_visible.split('.')[0])
        
        for i, diff in enumerate(self.differences):
            # Determine which line to use for positioning
            if diff['type'] == 'insert':
                target_line = diff['right_start']
            else:
                target_line = diff['left_start']
                
            # Get the y position of the target line
            bbox = None
            if diff['type'] == 'insert' or (diff['type'] == 'replace' and diff['left_start'] == 0):
                # Use right panel for positioning
                bbox = self.right_text.bbox(f"{target_line}.0")
            else:
                # Use left panel for positioning
                bbox = self.left_text.bbox(f"{target_line}.0")
                
            if bbox:
                y_pos = bbox[1] + bbox[3] // 2
                
                # Create a frame for the difference widget
                widget_frame = tk.Frame(self.middle_canvas, bg="#ffffff", relief=tk.RAISED, bd=1)
                
                # Determine style based on diff type
                if diff['type'] == 'delete':
                    color = "#e74c3c"
                    symbol = "−"
                    info = f"L{diff['left_start']}"
                    if diff['left_end'] > diff['left_start']:
                        info += f"-{diff['left_end']}"
                elif diff['type'] == 'insert':
                    color = "#00b894"
                    symbol = "+"
                    info = f"R{diff['right_start']}"
                    if diff['right_end'] > diff['right_start']:
                        info += f"-{diff['right_end']}"
                else:
                    color = "#f39c12"
                    symbol = "≠"
                    info = f"L{diff['left_start']}"
                    if diff['left_end'] > diff['left_start']:
                        info += f"-{diff['left_end']}"
                
                # Create info label
                info_label = tk.Label(widget_frame, text=f"{symbol} {info}", 
                                     bg="#ffffff", fg=color,
                                     font=("Segoe UI", 9, "bold"), cursor="hand2")
                info_label.pack(pady=2, padx=5)
                info_label.bind("<Button-1>", lambda e, idx=i: self.goto_diff(idx))
                
                # Button container
                btn_container = tk.Frame(widget_frame, bg="#ffffff")
                btn_container.pack(pady=2)
                
                # Add copy buttons
                if diff['type'] != 'insert':
                    btn = tk.Button(btn_container, text="Copy →", 
                                   command=lambda d=diff: self.copy_diff(d, "right"),
                                   bg="#0984e3", fg="white", bd=0,
                                   font=("Segoe UI", 8, "bold"),
                                   padx=8, pady=2, cursor="hand2")
                    btn.pack(side=tk.LEFT, padx=2)
                    self.add_hover_effect(btn, "#0984e3", "#74b9ff")
                    
                if diff['type'] != 'delete':
                    btn = tk.Button(btn_container, text="← Copy", 
                                   command=lambda d=diff: self.copy_diff(d, "left"),
                                   bg="#00b894", fg="white", bd=0,
                                   font=("Segoe UI", 8, "bold"),
                                   padx=8, pady=2, cursor="hand2")
                    btn.pack(side=tk.LEFT, padx=2)
                    self.add_hover_effect(btn, "#00b894", "#55efc4")
                
                # Create window on canvas at exact position
                self.middle_canvas.create_window(80, y_pos, window=widget_frame, anchor="center")
                
    def toggle_auto_compare(self):
        """Toggle auto compare mode"""
        self.auto_compare = not self.auto_compare
        
        if self.auto_compare:
            self.auto_btn.config(text="⚡ Auto: ON", bg="#00b894")
            self.add_hover_effect(self.auto_btn, "#00b894", "#55efc4")
        else:
            self.auto_btn.config(text="⚡ Auto: OFF", bg="#636e72")
            self.add_hover_effect(self.auto_btn, "#636e72", "#95a5a6")
            
        self.status_label.config(text=f"Auto-compare: {'enabled' if self.auto_compare else 'disabled'}")
        
        if self.auto_compare:
            self.schedule_compare()
        elif self.compare_timer:
            self.root.after_cancel(self.compare_timer)
            self.compare_timer = None
            
    def on_text_change(self):
        """Handle text changes"""
        self.update_line_numbers()
        
        if self.auto_compare:
            self.schedule_compare()
            
    def schedule_compare(self):
        """Schedule auto comparison"""
        if self.compare_timer:
            self.root.after_cancel(self.compare_timer)
        self.compare_timer = self.root.after(self.compare_delay, self.compare)
        
    def load_file(self, side):
        """Load file into panel"""
        filename = filedialog.askopenfilename(
            title=f"Open {side} file",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt"), 
                      ("Python files", "*.py"), ("JavaScript files", "*.js")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if side == "left":
                    self.left_text.delete(1.0, tk.END)
                    self.left_text.insert(1.0, content)
                    self.left_file = filename
                    self.left_title.config(text=f"Left: {os.path.basename(filename)}")
                else:
                    self.right_text.delete(1.0, tk.END)
                    self.right_text.insert(1.0, content)
                    self.right_file = filename
                    self.right_title.config(text=f"Right: {os.path.basename(filename)}")
                    
                self.update_line_numbers()
                self.status_label.config(text=f"Loaded: {os.path.basename(filename)}")
                self.save_to_history()
                
                if self.auto_compare and self.left_text.get(1.0, tk.END).strip() and self.right_text.get(1.0, tk.END).strip():
                    self.compare()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def compare(self):
        """Compare the two texts"""
        left_lines = self.left_text.get(1.0, "end-1c").splitlines()
        right_lines = self.right_text.get(1.0, "end-1c").splitlines()
        
        # Clear previous
        self.clear_highlights()
        self.differences = []
        self.middle_canvas.delete("all")
        
        # Get differences
        differ = difflib.SequenceMatcher(None, left_lines, right_lines)
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag != 'equal':
                self.differences.append({
                    'type': tag,
                    'left_start': i1 + 1,
                    'left_end': i2,
                    'right_start': j1 + 1,
                    'right_end': j2
                })
                
                # Highlight differences
                if tag == 'delete':
                    for i in range(i1, i2):
                        self.left_text.tag_add("removed", f"{i+1}.0", f"{i+1}.end")
                elif tag == 'insert':
                    for j in range(j1, j2):
                        self.right_text.tag_add("added", f"{j+1}.0", f"{j+1}.end")
                elif tag == 'replace':
                    for i in range(i1, i2):
                        self.left_text.tag_add("modified", f"{i+1}.0", f"{i+1}.end")
                    for j in range(j1, j2):
                        self.right_text.tag_add("modified", f"{j+1}.0", f"{j+1}.end")
        
        # Update middle panel
        self.update_middle_panel()
        
        # Update status
        if self.differences:
            self.info_label.config(text=f"🔍 {len(self.differences)} differences found")
            self.status_label.config(text=f"Comparison complete: {len(self.differences)} differences")
        else:
            self.info_label.config(text="✅ Files are identical")
            self.status_label.config(text="Files are identical")
            
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        
    def copy_diff(self, diff, direction):
        """Copy difference from one side to another"""
        self.save_to_history()
        
        try:
            if direction == "right":
                # Copy from left to right
                if diff['type'] == 'delete':
                    # Insert deleted lines into right
                    text = ""
                    for i in range(diff['left_start'], diff['left_end'] + 1):
                        if i <= int(self.left_text.index('end-1c').split('.')[0]):
                            line = self.left_text.get(f"{i}.0", f"{i}.end")
                            text += line + "\n"
                    self.right_text.insert(f"{diff['right_start']}.0", text)
                    
                elif diff['type'] == 'replace':
                    # Delete right lines and insert left lines
                    self.right_text.delete(f"{diff['right_start']}.0", f"{diff['right_end']}.end+1c")
                    text = ""
                    for i in range(diff['left_start'], diff['left_end'] + 1):
                        if i <= int(self.left_text.index('end-1c').split('.')[0]):
                            line = self.left_text.get(f"{i}.0", f"{i}.end")
                            text += line + "\n"
                    self.right_text.insert(f"{diff['right_start']}.0", text.rstrip() + "\n")
                    
            else:  # direction == "left"
                # Copy from right to left
                if diff['type'] == 'insert':
                    # Insert added lines into left
                    text = ""
                    for i in range(diff['right_start'], diff['right_end'] + 1):
                        if i <= int(self.right_text.index('end-1c').split('.')[0]):
                            line = self.right_text.get(f"{i}.0", f"{i}.end")
                            text += line + "\n"
                    self.left_text.insert(f"{diff['left_start']}.0", text)
                    
                elif diff['type'] == 'replace':
                    # Delete left lines and insert right lines
                    self.left_text.delete(f"{diff['left_start']}.0", f"{diff['left_end']}.end+1c")
                    text = ""
                    for i in range(diff['right_start'], diff['right_end'] + 1):
                        if i <= int(self.right_text.index('end-1c').split('.')[0]):
                            line = self.right_text.get(f"{i}.0", f"{i}.end")
                            text += line + "\n"
                    self.left_text.insert(f"{diff['left_start']}.0", text.rstrip() + "\n")
                    
            self.status_label.config(text=f"Copied difference to {'right' if direction == 'right' else 'left'}")
                    
        except Exception as e:
            print(f"Error copying diff: {e}")
            
        self.update_line_numbers()
        
        # Re-compare after change
        if self.auto_compare:
            self.schedule_compare()
        else:
            self.compare()
            
    def save_to_history(self):
        """Save current state for undo"""
        state = {
            'left': self.left_text.get(1.0, tk.END),
            'right': self.right_text.get(1.0, tk.END)
        }
        
        # Remove any states after current index
        self.history = self.history[:self.history_index + 1]
        
        # Add new state
        self.history.append(state)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1
            
    def undo(self):
        """Undo last action"""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            
            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(1.0, state['left'])
            self.right_text.delete(1.0, tk.END)
            self.right_text.insert(1.0, state['right'])
            
            self.update_line_numbers()
            self.status_label.config(text="Undo performed")
            
            if self.auto_compare:
                self.schedule_compare()
            
    def clear_highlights(self):
        """Clear all highlights"""
        for tag in ["added", "removed", "modified", "current"]:
            self.left_text.tag_remove(tag, 1.0, tk.END)
            self.right_text.tag_remove(tag, 1.0, tk.END)
            
    def goto_diff(self, index):
        """Go to specific difference"""
        if 0 <= index < len(self.differences):
            self.current_diff = index
            diff = self.differences[index]
            
            # Clear current highlights
            self.left_text.tag_remove("current", 1.0, tk.END)
            self.right_text.tag_remove("current", 1.0, tk.END)
            
            # Highlight and scroll to difference
            if diff['left_end'] >= diff['left_start']:
                self.left_text.see(f"{diff['left_start']}.0")
                self.left_text.tag_add("current", f"{diff['left_start']}.0", f"{diff['left_end'] + 1}.0")
                
            if diff['right_end'] >= diff['right_start']:
                self.right_text.see(f"{diff['right_start']}.0")
                self.right_text.tag_add("current", f"{diff['right_start']}.0", f"{diff['right_end'] + 1}.0")
                
            self.status_label.config(text=f"Viewing difference {index + 1} of {len(self.differences)}")
            
    def next_diff(self):
        """Go to next difference"""
        if self.differences:
            if self.current_diff < len(self.differences) - 1:
                self.goto_diff(self.current_diff + 1)
            else:
                self.goto_diff(0)
                
    def prev_diff(self):
        """Go to previous difference"""
        if self.differences:
            if self.current_diff > 0:
                self.goto_diff(self.current_diff - 1)
            else:
                self.goto_diff(len(self.differences) - 1)


def main():
    root = tk.Tk()
    app = ModernDiffApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
