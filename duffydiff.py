import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import difflib
import os
from datetime import datetime
import json

class ModernDiffApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DuffyDiff Pro 2.0 - Auto Compare")
        self.root.geometry("1600x900")
        
        # Auto-compare settings
        self.auto_compare = True
        self.compare_delay = 500  # milliseconds
        self.compare_timer = None
        
        # Theme configuration
        self.dark_mode = False
        self.themes = {
            "light": {
                "bg": "#FFFFFF",
                "fg": "#212529",
                "panel_bg": "#F8F9FA",
                "text_bg": "#FFFFFF",
                "text_fg": "#212529",
                "added": "#D4EDDA",
                "removed": "#F8D7DA",
                "modified": "#FFF3CD",
                "line_bg": "#E9ECEF",
                "button_bg": "#007BFF",
                "button_hover": "#0056B3",
                "header_bg": "#343A40",
                "header_fg": "#FFFFFF",
                "border": "#DEE2E6",
                "highlight": "#FFC107"
            },
            "dark": {
                "bg": "#1E1E1E",
                "fg": "#E0E0E0",
                "panel_bg": "#252525",
                "text_bg": "#2D2D2D",
                "text_fg": "#E0E0E0",
                "added": "#1B5E20",
                "removed": "#B71C1C",
                "modified": "#F57C00",
                "line_bg": "#3E3E3E",
                "button_bg": "#2196F3",
                "button_hover": "#1976D2",
                "header_bg": "#161616",
                "header_fg": "#FFFFFF",
                "border": "#404040",
                "highlight": "#FFD700"
            }
        }
        
        # File management
        self.left_file = None
        self.right_file = None
        
        # Diff tracking
        self.differences = []
        self.current_diff = -1
        
        # History for undo/redo
        self.history = []
        self.history_index = -1
        self.max_history = 50
        
        # Sync scroll flag
        self.sync_scroll = True
        self.is_syncing = False
        
        # Track if we're in the middle of an update
        self.is_updating = False
        
        # Initialize UI
        self.setup_styles()
        self.create_menu()
        self.create_toolbar()
        self.create_main_panels()
        self.create_statusbar()
        self.setup_bindings()
        
        # Apply initial theme
        self.apply_theme()
        
        # Start auto-compare if enabled
        if self.auto_compare:
            self.schedule_compare()
    
    def setup_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
    def apply_theme(self):
        """Apply selected theme to all widgets"""
        theme = self.themes["dark" if self.dark_mode else "light"]
        
        # Configure root
        self.root.configure(bg=theme["bg"])
        
        # Configure styles
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("Header.TFrame", background=theme["header_bg"])
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("Header.TLabel", background=theme["header_bg"], foreground=theme["header_fg"])
        self.style.configure("TButton", background=theme["button_bg"], foreground="#FFFFFF")
        
        # Update text widgets if they exist
        if hasattr(self, 'left_text'):
            self.left_text.configure(
                bg=theme["text_bg"],
                fg=theme["text_fg"],
                insertbackground=theme["fg"]
            )
            self.right_text.configure(
                bg=theme["text_bg"],
                fg=theme["text_fg"],
                insertbackground=theme["fg"]
            )
            
            # Update line numbers
            self.left_lines.configure(
                bg=theme["line_bg"],
                fg=theme["fg"]
            )
            self.right_lines.configure(
                bg=theme["line_bg"],
                fg=theme["fg"]
            )
            
            # Update diff colors
            self.configure_tags()
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Left", command=lambda: self.load_file("left"), accelerator="Ctrl+O")
        file_menu.add_command(label="Open Right", command=lambda: self.load_file("right"), accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Left", command=lambda: self.save_file("left"), accelerator="Ctrl+S")
        file_menu.add_command(label="Save Right", command=lambda: self.save_file("right"), accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Diff", command=self.export_diff)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_dialog, accelerator="Ctrl+H")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Dark Mode", command=self.toggle_theme)
        view_menu.add_checkbutton(label="Sync Scroll", command=self.toggle_sync_scroll, variable=tk.BooleanVar(value=True))
        view_menu.add_checkbutton(label="Auto Compare", command=self.toggle_auto_compare, variable=tk.BooleanVar(value=True))
        view_menu.add_separator()
        view_menu.add_command(label="Next Difference", command=self.next_diff, accelerator="F3")
        view_menu.add_command(label="Previous Difference", command=self.prev_diff, accelerator="Shift+F3")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Manual Compare", command=self.compare, accelerator="F5")
        tools_menu.add_command(label="Clear All", command=self.clear_all)
        tools_menu.add_separator()
        tools_menu.add_command(label="Merge Left → Right", command=lambda: self.merge_all("right"))
        tools_menu.add_command(label="Merge Right → Left", command=lambda: self.merge_all("left"))
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings", command=self.open_settings)
        
    def create_toolbar(self):
        """Create toolbar with main actions"""
        toolbar = ttk.Frame(self.root, style="Header.TFrame")
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Create modern buttons
        self.create_toolbar_button(toolbar, "📁 Open Left", lambda: self.load_file("left"))
        self.create_toolbar_button(toolbar, "📁 Open Right", lambda: self.load_file("right"))
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Auto-compare toggle button
        self.auto_compare_btn = self.create_toolbar_button(
            toolbar, 
            "🔄 Auto: ON" if self.auto_compare else "🔄 Auto: OFF", 
            self.toggle_auto_compare, 
            "#28A745" if self.auto_compare else "#6C757D"
        )
        
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.create_toolbar_button(toolbar, "⬅ Prev", self.prev_diff, "#FFC107")
        self.create_toolbar_button(toolbar, "➡ Next", self.next_diff, "#FFC107")
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.create_toolbar_button(toolbar, "↶ Undo", self.undo, "#DC3545")
        self.create_toolbar_button(toolbar, "↷ Redo", self.redo, "#DC3545")
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.create_toolbar_button(toolbar, "💾 Save", lambda: self.save_file(self.get_active_panel()))
        
        # Right side info
        info_frame = ttk.Frame(toolbar, style="Header.TFrame")
        info_frame.pack(side=tk.RIGHT, padx=10)
        
        self.diff_info = ttk.Label(info_frame, text="No differences", style="Header.TLabel")
        self.diff_info.pack()
        
        self.auto_status = ttk.Label(
            info_frame, 
            text="🟢 Auto-compare: ON" if self.auto_compare else "🔴 Auto-compare: OFF", 
            style="Header.TLabel",
            font=("Segoe UI", 9)
        )
        self.auto_status.pack()
        
    def create_toolbar_button(self, parent, text, command, color="#007BFF"):
        """Create a modern toolbar button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Hover effect
        btn.bind("<Enter>", lambda e: btn.configure(relief=tk.RAISED))
        btn.bind("<Leave>", lambda e: btn.configure(relief=tk.FLAT))
        
        return btn
    
    def create_main_panels(self):
        """Create the main text panels"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel
        left_frame = ttk.Frame(main_container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=2)
        
        # Left header
        left_header = ttk.Frame(left_frame)
        left_header.pack(fill=tk.X)
        
        self.left_title = ttk.Label(left_header, text="Left Panel - No File", font=("Segoe UI", 11, "bold"))
        self.left_title.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Left text container
        left_text_frame = ttk.Frame(left_frame)
        left_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left line numbers
        self.left_lines = tk.Text(
            left_text_frame,
            width=5,
            padx=5,
            pady=5,
            state=tk.DISABLED,
            font=("Consolas", 11),
            relief=tk.FLAT
        )
        self.left_lines.pack(side=tk.LEFT, fill=tk.Y)
        
        # Left text widget
        self.left_text = tk.Text(
            left_text_frame,
            wrap=tk.NONE,
            padx=5,
            pady=5,
            font=("Consolas", 11),
            undo=True,
            maxundo=20
        )
        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Left scrollbars
        left_vscroll = ttk.Scrollbar(left_text_frame, orient=tk.VERTICAL, command=self.left_text.yview)
        left_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_text.config(yscrollcommand=lambda *args: self.sync_vertical_scroll(left_vscroll, *args))
        
        left_hscroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.left_text.xview)
        left_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.left_text.config(xscrollcommand=lambda *args: self.sync_horizontal_scroll(left_hscroll, *args))
        
        # Middle control panel
        middle_frame = ttk.Frame(main_container)
        middle_frame.grid(row=0, column=1, sticky="ns", padx=5)
        
        # Middle header
        ttk.Label(middle_frame, text="Actions", font=("Segoe UI", 11, "bold")).pack(pady=5)
        
        # Quick stats
        self.stats_frame = ttk.Frame(middle_frame)
        self.stats_frame.pack(pady=10)
        
        self.stats_label = ttk.Label(self.stats_frame, text="Ready", font=("Segoe UI", 9))
        self.stats_label.pack()
        
        # Control buttons container with scrollbar
        canvas = tk.Canvas(middle_frame, width=120)
        scrollbar = ttk.Scrollbar(middle_frame, orient="vertical", command=canvas.yview)
        self.controls_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=self.controls_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.controls_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Right panel
        right_frame = ttk.Frame(main_container)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=2)
        
        # Right header
        right_header = ttk.Frame(right_frame)
        right_header.pack(fill=tk.X)
        
        self.right_title = ttk.Label(right_header, text="Right Panel - No File", font=("Segoe UI", 11, "bold"))
        self.right_title.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Right text container
        right_text_frame = ttk.Frame(right_frame)
        right_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Right line numbers
        self.right_lines = tk.Text(
            right_text_frame,
            width=5,
            padx=5,
            pady=5,
            state=tk.DISABLED,
            font=("Consolas", 11),
            relief=tk.FLAT
        )
        self.right_lines.pack(side=tk.LEFT, fill=tk.Y)
        
        # Right text widget
        self.right_text = tk.Text(
            right_text_frame,
            wrap=tk.NONE,
            padx=5,
            pady=5,
            font=("Consolas", 11),
            undo=True,
            maxundo=20
        )
        self.right_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right scrollbars
        right_vscroll = ttk.Scrollbar(right_text_frame, orient=tk.VERTICAL, command=self.right_text.yview)
        right_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_text.config(yscrollcommand=lambda *args: self.sync_vertical_scroll(right_vscroll, *args))
        
        right_hscroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.right_text.xview)
        right_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.right_text.config(xscrollcommand=lambda *args: self.sync_horizontal_scroll(right_hscroll, *args))
        
        # Configure grid weights
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Configure tags for highlighting
        self.configure_tags()
        
        # Bind text changes for auto-compare
        self.left_text.bind("<<Modified>>", lambda e: self.on_text_change("left"))
        self.right_text.bind("<<Modified>>", lambda e: self.on_text_change("right"))
        self.left_text.bind("<KeyRelease>", lambda e: self.on_text_change("left"))
        self.right_text.bind("<KeyRelease>", lambda e: self.on_text_change("right"))
        
        # Enable drag and drop
        self.setup_drag_drop()
        
    def configure_tags(self):
        """Configure text tags for diff highlighting"""
        theme = self.themes["dark" if self.dark_mode else "light"]
        
        # Left text tags
        self.left_text.tag_configure("added", background=theme["added"])
        self.left_text.tag_configure("removed", background=theme["removed"])
        self.left_text.tag_configure("modified", background=theme["modified"])
        self.left_text.tag_configure("current", background=theme["highlight"])
        
        # Right text tags
        self.right_text.tag_configure("added", background=theme["added"])
        self.right_text.tag_configure("removed", background=theme["removed"])
        self.right_text.tag_configure("modified", background=theme["modified"])
        self.right_text.tag_configure("current", background=theme["highlight"])
        
    def create_statusbar(self):
        """Create status bar"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_left = ttk.Label(self.statusbar, text="Ready")
        self.status_left.pack(side=tk.LEFT, padx=10)
        
        self.status_center = ttk.Label(self.statusbar, text="")
        self.status_center.pack(side=tk.LEFT, expand=True)
        
        self.status_right = ttk.Label(self.statusbar, text="")
        self.status_right.pack(side=tk.RIGHT, padx=10)
        
    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-o>", lambda e: self.load_file("left"))
        self.root.bind("<Control-O>", lambda e: self.load_file("right"))
        self.root.bind("<Control-s>", lambda e: self.save_file("left"))
        self.root.bind("<Control-S>", lambda e: self.save_file("right"))
        self.root.bind("<F5>", lambda e: self.compare())
        self.root.bind("<F3>", lambda e: self.next_diff())
        self.root.bind("<Shift-F3>", lambda e: self.prev_diff())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-f>", lambda e: self.find_dialog())
        self.root.bind("<Control-h>", lambda e: self.replace_dialog())
        self.root.bind("<Control-a>", lambda e: self.toggle_auto_compare())
        
    def setup_drag_drop(self):
        """Enable drag and drop for files"""
        # This would require tkinterdnd2 library for full implementation
        pass
        
    def sync_vertical_scroll(self, scrollbar, first, last):
        """Synchronize vertical scrolling"""
        scrollbar.set(first, last)
        if self.sync_scroll and not self.is_syncing:
            self.is_syncing = True
            # Sync the other text widget
            if scrollbar.master.master == self.left_text.master:
                self.right_text.yview_moveto(first)
            else:
                self.left_text.yview_moveto(first)
            self.is_syncing = False
            
    def sync_horizontal_scroll(self, scrollbar, first, last):
        """Synchronize horizontal scrolling"""
        scrollbar.set(first, last)
        if self.sync_scroll and not self.is_syncing:
            self.is_syncing = True
            # Sync the other text widget
            if scrollbar.master == self.left_text.master.master:
                self.right_text.xview_moveto(first)
            else:
                self.left_text.xview_moveto(first)
            self.is_syncing = False
            
    def toggle_sync_scroll(self):
        """Toggle scroll synchronization"""
        self.sync_scroll = not self.sync_scroll
        self.status_left.config(text=f"Sync Scroll: {'ON' if self.sync_scroll else 'OFF'}")
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
    def toggle_auto_compare(self):
        """Toggle auto-compare feature"""
        self.auto_compare = not self.auto_compare
        
        # Update UI
        if self.auto_compare:
            self.auto_compare_btn.configure(text="🔄 Auto: ON", bg="#28A745")
            self.auto_status.config(text="🟢 Auto-compare: ON")
            self.status_center.config(text="Auto-compare enabled")
            # Start auto-compare
            self.schedule_compare()
        else:
            self.auto_compare_btn.configure(text="🔄 Auto: OFF", bg="#6C757D")
            self.auto_status.config(text="🔴 Auto-compare: OFF")
            self.status_center.config(text="Auto-compare disabled")
            # Cancel pending compare
            if self.compare_timer:
                self.root.after_cancel(self.compare_timer)
                self.compare_timer = None
        
    def on_text_change(self, side):
        """Handle text changes"""
        if self.is_updating:
            return
            
        self.update_line_numbers(side)
        
        # Schedule auto-compare if enabled
        if self.auto_compare:
            self.schedule_compare()
        
    def schedule_compare(self):
        """Schedule an automatic comparison after a delay"""
        if not self.auto_compare:
            return
            
        # Cancel previous timer if exists
        if self.compare_timer:
            self.root.after_cancel(self.compare_timer)
            
        # Schedule new compare
        self.compare_timer = self.root.after(self.compare_delay, self.auto_compare_texts)
        
    def auto_compare_texts(self):
        """Perform automatic comparison"""
        if self.auto_compare:
            self.compare(auto=True)
            self.compare_timer = None
        
    def update_line_numbers(self, side=None):
        """Update line numbers for text widgets"""
        if side == "left" or side is None:
            self.update_single_line_numbers(self.left_text, self.left_lines)
        if side == "right" or side is None:
            self.update_single_line_numbers(self.right_text, self.right_lines)
            
    def update_single_line_numbers(self, text_widget, line_widget):
        """Update line numbers for a single text widget"""
        line_widget.config(state=tk.NORMAL)
        line_widget.delete(1.0, tk.END)
        
        lines = text_widget.get(1.0, tk.END).count('\n')
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        line_widget.insert(1.0, line_numbers)
        line_widget.config(state=tk.DISABLED)
        
    def load_file(self, side):
        """Load file into panel"""
        filename = filedialog.askopenfilename(
            title=f"Open {side.capitalize()} File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.is_updating = True
                    
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
                    
                self.is_updating = False
                    
                self.update_line_numbers(side)
                self.status_left.config(text=f"Loaded: {os.path.basename(filename)}")
                self.save_to_history()
                
                # Auto-compare if both panels have content
                if self.auto_compare:
                    left_content = self.left_text.get(1.0, tk.END).strip()
                    right_content = self.right_text.get(1.0, tk.END).strip()
                    if left_content and right_content:
                        self.compare(auto=True)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            finally:
                self.is_updating = False
                
    def save_file(self, side):
        """Save file from panel"""
        if not side:
            side = self.get_active_panel()
            
        if not side:
            messagebox.showwarning("Warning", "Please select a panel to save")
            return
            
        filename = filedialog.asksaveasfilename(
            title=f"Save {side.capitalize()} File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.left_text.get(1.0, tk.END) if side == "left" else self.right_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content.rstrip())
                    
                if side == "left":
                    self.left_file = filename
                    self.left_title.config(text=f"Left: {os.path.basename(filename)}")
                else:
                    self.right_file = filename
                    self.right_title.config(text=f"Right: {os.path.basename(filename)}")
                    
                self.status_left.config(text=f"Saved: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                
    def get_active_panel(self):
        """Get currently active panel"""
        focus = self.root.focus_get()
        if focus == self.left_text:
            return "left"
        elif focus == self.right_text:
            return "right"
        return None
        
    def compare(self, auto=False):
        """Compare the two text panels"""
        left_lines = self.left_text.get(1.0, tk.END).splitlines()
        right_lines = self.right_text.get(1.0, tk.END).splitlines()
        
        # Don't compare if both panels are empty
        if not any(left_lines) and not any(right_lines):
            return
            
        # Clear previous highlights
        self.clear_highlights()
        
        # Clear control buttons
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
            
        self.differences = []
        
        # Perform diff
        differ = difflib.SequenceMatcher(None, left_lines, right_lines)
        
        added_count = 0
        removed_count = 0
        modified_count = 0
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag != 'equal':
                diff_data = {
                    'type': tag,
                    'left_start': i1 + 1,
                    'left_end': i2,
                    'right_start': j1 + 1,
                    'right_end': j2
                }
                self.differences.append(diff_data)
                
                # Highlight differences
                if tag == 'delete':
                    removed_count += (i2 - i1)
                    for i in range(i1, i2):
                        self.left_text.tag_add("removed", f"{i+1}.0", f"{i+1}.end")
                elif tag == 'insert':
                    added_count += (j2 - j1)
                    for j in range(j1, j2):
                        self.right_text.tag_add("added", f"{j+1}.0", f"{j+1}.end")
                elif tag == 'replace':
                    modified_count += max(i2 - i1, j2 - j1)
                    for i in range(i1, i2):
                        self.left_text.tag_add("modified", f"{i+1}.0", f"{i+1}.end")
                    for j in range(j1, j2):
                        self.right_text.tag_add("modified", f"{j+1}.0", f"{j+1}.end")
                        
                # Create control button
                self.create_diff_control(diff_data, len(self.differences))
                
        # Update status
        if self.differences:
            diff_text = f"{len(self.differences)} differences"
            if not auto:
                diff_text += f" (➕{added_count} ➖{removed_count} ✏️{modified_count})"
            self.diff_info.config(text=diff_text)
            self.stats_label.config(text=f"Total: {len(self.differences)}")
            
            # Update statusbar with details
            self.status_left.config(text=f"Differences: {len(self.differences)}")
            if auto:
                self.status_center.config(text="Auto-compared")
        else:
            self.diff_info.config(text="Files are identical ✓")
            self.stats_label.config(text="Identical")
            self.status_left.config(text="No differences found")
            self.status_center.config(text="Files match")
            
        # Update status right with timestamp
        compare_time = datetime.now().strftime("%H:%M:%S")
        self.status_right.config(text=f"Last compare: {compare_time}")
            
    def create_diff_control(self, diff_data, index):
        """Create control buttons for a difference"""
        frame = ttk.Frame(self.controls_frame)
        frame.pack(fill=tk.X, pady=2)
        
        # Diff info with better formatting
        if diff_data['type'] == 'delete':
            icon = "🗑️"
            label = f"#{index}: Removed"
            lines = f"L{diff_data['left_start']}"
            if diff_data['left_end'] > diff_data['left_start']:
                lines += f"-{diff_data['left_end']}"
            color = "#DC3545"
        elif diff_data['type'] == 'insert':
            icon = "➕"
            label = f"#{index}: Added"
            lines = f"R{diff_data['right_start']}"
            if diff_data['right_end'] > diff_data['right_start']:
                lines += f"-{diff_data['right_end']}"
            color = "#28A745"
        else:
            icon = "✏️"
            label = f"#{index}: Modified"
            lines = f"L{diff_data['left_start']}"
            if diff_data['left_end'] > diff_data['left_start']:
                lines += f"-{diff_data['left_end']}"
            color = "#FFC107"
            
        # Create info label with icon
        info_text = f"{icon} {label}\n{lines}"
        ttk.Label(frame, text=info_text, font=("Segoe UI", 8)).pack()
        
        # Action buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        
        # Navigation button
        tk.Button(
            btn_frame,
            text="Go",
            command=lambda: self.goto_diff(index - 1),
            bg="#6C757D",
            fg="white",
            width=4,
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI", 8)
        ).pack(side=tk.LEFT, padx=1)
        
        if diff_data['type'] != 'insert':
            tk.Button(
                btn_frame,
                text="→",
                command=lambda: self.copy_diff(diff_data, "right"),
                bg="#007BFF",
                fg="white",
                width=3,
                relief=tk.FLAT,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=1)
            
        if diff_data['type'] != 'delete':
            tk.Button(
                btn_frame,
                text="←",
                command=lambda: self.copy_diff(diff_data, "left"),
                bg="#28A745",
                fg="white",
                width=3,
                relief=tk.FLAT,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=1)
            
    def goto_diff(self, index):
        """Go to a specific difference"""
        if 0 <= index < len(self.differences):
            self.current_diff = index
            self.highlight_current_diff()
            
    def copy_diff(self, diff_data, direction):
        """Copy difference from one panel to another"""
        self.is_updating = True
        self.save_to_history()
        
        if direction == "right":
            # Copy from left to right
            text = ""
            for i in range(diff_data['left_start'], diff_data['left_end'] + 1):
                line = self.left_text.get(f"{i}.0", f"{i}.end")
                if line:
                    text += line + "\n"
                    
            # Delete existing lines in right
            if diff_data['right_end'] >= diff_data['right_start']:
                self.right_text.delete(f"{diff_data['right_start']}.0", f"{diff_data['right_end']+1}.0")
                
            # Insert new text
            self.right_text.insert(f"{diff_data['right_start']}.0", text)
            
        else:
            # Copy from right to left
            text = ""
            for i in range(diff_data['right_start'], diff_data['right_end'] + 1):
                line = self.right_text.get(f"{i}.0", f"{i}.end")
                if line:
                    text += line + "\n"
                    
            # Delete existing lines in left
            if diff_data['left_end'] >= diff_data['left_start']:
                self.left_text.delete(f"{diff_data['left_start']}.0", f"{diff_data['left_end']+1}.0")
                
            # Insert new text
            self.left_text.insert(f"{diff_data['left_start']}.0", text)
            
        self.is_updating = False
        self.update_line_numbers()
        
        # Re-compare after change
        if self.auto_compare:
            self.schedule_compare()
        else:
            self.compare()
        
    def clear_highlights(self):
        """Clear all highlighting"""
        for tag in ["added", "removed", "modified", "current"]:
            self.left_text.tag_remove(tag, 1.0, tk.END)
            self.right_text.tag_remove(tag, 1.0, tk.END)
            
    def highlight_current_diff(self):
        """Highlight current difference"""
        if not self.differences or self.current_diff < 0:
            return
            
        diff = self.differences[self.current_diff]
        
        # Clear previous current highlight
        self.left_text.tag_remove("current", 1.0, tk.END)
        self.right_text.tag_remove("current", 1.0, tk.END)
        
        # Add current highlight
        if diff['left_end'] >= diff['left_start']:
            self.left_text.tag_add("current", f"{diff['left_start']}.0", f"{diff['left_end']+1}.0")
            self.left_text.see(f"{diff['left_start']}.0")
            
        if diff['right_end'] >= diff['right_start']:
            self.right_text.tag_add("current", f"{diff['right_start']}.0", f"{diff['right_end']+1}.0")
            self.right_text.see(f"{diff['right_start']}.0")
            
        self.status_right.config(text=f"Viewing: {self.current_diff + 1}/{len(self.differences)}")
        
    def next_diff(self):
        """Navigate to next difference"""
        if self.differences and self.current_diff < len(self.differences) - 1:
            self.current_diff += 1
            self.highlight_current_diff()
            
    def prev_diff(self):
        """Navigate to previous difference"""
        if self.differences and self.current_diff > 0:
            self.current_diff -= 1
            self.highlight_current_diff()
            
    def merge_all(self, direction):
        """Merge all differences in one direction"""
        if not self.differences:
            messagebox.showinfo("Info", "No differences to merge")
            return
            
        msg = f"Merge all differences to the {direction} panel?"
        if not messagebox.askyesno("Confirm", msg):
            return
            
        self.is_updating = True
        self.save_to_history()
        
        if direction == "right":
            content = self.left_text.get(1.0, tk.END)
            self.right_text.delete(1.0, tk.END)
            self.right_text.insert(1.0, content)
        else:
            content = self.right_text.get(1.0, tk.END)
            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(1.0, content)
            
        self.is_updating = False
        self.update_line_numbers()
        
        if self.auto_compare:
            self.schedule_compare()
        else:
            self.compare()
        
    def save_to_history(self):
        """Save current state to history"""
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
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
            
    def undo(self):
        """Undo last action"""
        if self.history_index > 0:
            self.is_updating = True
            self.history_index -= 1
            state = self.history[self.history_index]
            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(1.0, state['left'])
            self.right_text.delete(1.0, tk.END)
            self.right_text.insert(1.0, state['right'])
            self.is_updating = False
            self.update_line_numbers()
            self.status_left.config(text="Undo performed")
            
            if self.auto_compare:
                self.schedule_compare()
            
    def redo(self):
        """Redo last undone action"""
        if self.history_index < len(self.history) - 1:
            self.is_updating = True
            self.history_index += 1
            state = self.history[self.history_index]
            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(1.0, state['left'])
            self.right_text.delete(1.0, tk.END)
            self.right_text.insert(1.0, state['right'])
            self.is_updating = False
            self.update_line_numbers()
            self.status_left.config(text="Redo performed")
            
            if self.auto_compare:
                self.schedule_compare()
            
    def clear_all(self):
        """Clear all panels"""
        if messagebox.askyesno("Confirm", "Clear all panels?"):
            self.is_updating = True
            self.save_to_history()
            self.left_text.delete(1.0, tk.END)
            self.right_text.delete(1.0, tk.END)
            self.left_file = None
            self.right_file = None
            self.left_title.config(text="Left Panel - No File")
            self.right_title.config(text="Right Panel - No File")
            self.is_updating = False
            self.update_line_numbers()
            self.clear_highlights()
            for widget in self.controls_frame.winfo_children():
                widget.destroy()
            self.differences = []
            self.current_diff = -1
            self.diff_info.config(text="No differences")
            self.stats_label.config(text="Ready")
            self.status_left.config(text="Panels cleared")
            
    def open_settings(self):
        """Open settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        # Auto-compare delay setting
        ttk.Label(dialog, text="Auto-compare delay (ms):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        delay_var = tk.StringVar(value=str(self.compare_delay))
        delay_entry = ttk.Entry(dialog, textvariable=delay_var, width=10)
        delay_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Font size setting
        ttk.Label(dialog, text="Font size:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        font_var = tk.StringVar(value="11")
        font_spinbox = ttk.Spinbox(dialog, from_=8, to=20, textvariable=font_var, width=10)
        font_spinbox.grid(row=1, column=1, padx=10, pady=10)
        
        def apply_settings():
            try:
                self.compare_delay = int(delay_var.get())
                font_size = int(font_var.get())
                
                # Update font size
                new_font = ("Consolas", font_size)
                self.left_text.configure(font=new_font)
                self.right_text.configure(font=new_font)
                self.left_lines.configure(font=new_font)
                self.right_lines.configure(font=new_font)
                
                messagebox.showinfo("Success", "Settings applied")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid values")
                
        ttk.Button(dialog, text="Apply", command=apply_settings).grid(row=3, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=3, column=1, padx=10, pady=20)
            
    def find_dialog(self):
        """Open find dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Find")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        find_entry = ttk.Entry(dialog, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)
        find_entry.focus()
        
        def find_text():
            text = find_entry.get()
            if not text:
                return
                
            # Search in active panel
            widget = self.left_text if self.get_active_panel() == "left" else self.right_text
            
            # Clear previous search highlights
            widget.tag_remove("search", 1.0, tk.END)
            
            # Search and highlight
            start = 1.0
            count = 0
            while True:
                pos = widget.search(text, start, tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(text)}c"
                widget.tag_add("search", pos, end)
                widget.tag_config("search", background="yellow")
                start = end
                count += 1
                
            # Go to first occurrence
            first = widget.search(text, 1.0, tk.END)
            if first:
                widget.see(first)
                self.status_center.config(text=f"Found {count} occurrences")
            else:
                self.status_center.config(text="Text not found")
                
        ttk.Button(dialog, text="Find", command=find_text).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=1, column=2, padx=5, pady=5)
        
    def replace_dialog(self):
        """Open replace dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Replace")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        find_entry = ttk.Entry(dialog, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(dialog, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        replace_entry = ttk.Entry(dialog, width=30)
        replace_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        def replace_all():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            
            if not find_text:
                return
                
            widget = self.left_text if self.get_active_panel() == "left" else self.right_text
            content = widget.get(1.0, tk.END)
            new_content = content.replace(find_text, replace_text)
            
            if content != new_content:
                self.is_updating = True
                self.save_to_history()
                widget.delete(1.0, tk.END)
                widget.insert(1.0, new_content)
                self.is_updating = False
                self.update_line_numbers()
                count = content.count(find_text)
                messagebox.showinfo("Replace", f"Replaced {count} occurrences")
                dialog.destroy()
                
                if self.auto_compare:
                    self.schedule_compare()
                
        ttk.Button(dialog, text="Replace All", command=replace_all).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=2, column=2, padx=5, pady=5)
        
    def export_diff(self):
        """Export differences to file"""
        if not self.differences:
            messagebox.showinfo("Info", "No differences to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Differences",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("HTML files", "*.html"), ("JSON files", "*.json")]
        )
        
        if filename:
            try:
                ext = os.path.splitext(filename)[1].lower()
                
                if ext == ".json":
                    with open(filename, 'w') as f:
                        json.dump(self.differences, f, indent=2)
                elif ext == ".html":
                    self.export_html(filename)
                else:
                    self.export_text(filename)
                    
                messagebox.showinfo("Success", f"Differences exported to {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
                
    def export_text(self, filename):
        """Export differences as text"""
        with open(filename, 'w') as f:
            f.write(f"Diff Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Left file: {self.left_file or 'Untitled'}\n")
            f.write(f"Right file: {self.right_file or 'Untitled'}\n")
            f.write(f"Total differences: {len(self.differences)}\n\n")
            
            for i, diff in enumerate(self.differences, 1):
                f.write(f"Difference #{i}\n")
                f.write(f"Type: {diff['type']}\n")
                f.write(f"Left: Lines {diff['left_start']}-{diff['left_end']}\n")
                f.write(f"Right: Lines {diff['right_start']}-{diff['right_end']}\n")
                f.write("-" * 30 + "\n")
                
    def export_html(self, filename):
        """Export differences as HTML"""
        html = f"""
        <html>
        <head>
            <title>Diff Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .info {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .diff {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .added {{ background-color: #d4edda; border-color: #28a745; }}
                .removed {{ background-color: #f8d7da; border-color: #dc3545; }}
                .modified {{ background-color: #fff3cd; border-color: #ffc107; }}
                .diff h3 {{ margin-top: 0; }}
            </style>
        </head>
        <body>
            <h1>Diff Report</h1>
            <div class="info">
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Left file:</strong> {self.left_file or 'Untitled'}</p>
                <p><strong>Right file:</strong> {self.right_file or 'Untitled'}</p>
                <p><strong>Total differences:</strong> {len(self.differences)}</p>
            </div>
        """
        
        for i, diff in enumerate(self.differences, 1):
            css_class = "added" if diff['type'] == "insert" else "removed" if diff['type'] == "delete" else "modified"
            html += f"""
            <div class="diff {css_class}">
                <h3>Difference #{i}</h3>
                <p><strong>Type:</strong> {diff['type'].capitalize()}</p>
                <p><strong>Left:</strong> Lines {diff['left_start']}-{diff['left_end']}</p>
                <p><strong>Right:</strong> Lines {diff['right_start']}-{diff['right_end']}</p>
            </div>
            """
            
        html += "</body></html>"
        
        with open(filename, 'w') as f:
            f.write(html)


def main():
    root = tk.Tk()
    app = ModernDiffApp(root)
    
    # Set window icon if available
    try:
        root.iconbitmap("diff.ico")
    except:
        pass
        
    root.mainloop()


if __name__ == "__main__":
    main()
