# DuffyDiff

<div align="center">
  
![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**A modern, professional text comparison tool with real-time auto-compare functionality**

</div>

---

## ✨ What's New in 2.0

### 🔄 **Auto-Compare Technology**
- **Real-time comparison** - No more clicking! Changes are detected and compared automatically
- **Smart debouncing** - Configurable delay (default 500ms) prevents excessive comparisons
- **Visual indicators** - Green/red status shows when auto-compare is active
- **Toggle control** - Easily switch between automatic and manual modes

### 🎨 **Modern Professional Interface**
- **Dual theme support** - Light and dark modes for comfortable viewing
- **Enhanced highlighting** - Clear color coding for added, removed, and modified content
- **Responsive design** - Adapts to different screen sizes
- **Smooth animations** - Hover effects and visual feedback

---

## 🚀 Key Features

### Core Functionality
- ✅ **Side-by-side comparison** with synchronized scrolling
- ✅ **Line-by-line differences** with precise highlighting
- ✅ **Bidirectional merging** - Copy changes in either direction
- ✅ **Smart navigation** - Jump between differences with F3/Shift+F3
- ✅ **Multiple merge options** - Individual changes or bulk operations

### Advanced Features
- 📝 **Full undo/redo support** with 50-state history
- 🔍 **Find & Replace** functionality (Ctrl+F / Ctrl+H)
- 💾 **Multiple export formats** - TXT, HTML, JSON
- 📊 **Real-time statistics** - Track additions, deletions, modifications
- ⏱️ **Timestamp tracking** - See when comparisons occurred

### User Experience
- 🎯 **Intelligent line numbering** - Updates automatically
- 🔗 **Synchronized scrolling** - Keep panels aligned (toggleable)
- 📌 **Difference navigation** - Click to jump to any difference
- 🎨 **Color-coded differences**:
  - 🟢 **Green** - Added content
  - 🔴 **Red** - Removed content  
  - 🟡 **Yellow** - Modified content
  - 🟠 **Orange** - Current selection

---

## 📦 Installation

### Prerequisites
```bash
# Python 3.6 or higher required
python --version

# Tkinter (usually pre-installed with Python)
python -m tkinter
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/JustVugg/duffydiff-pro.git
cd duffydiff-pro

# Run the application
python duffydiff_pro.py
```

### Optional Dependencies
```bash
# For enhanced drag-and-drop support (optional)
pip install tkinterdnd2
```

---

## 📖 Usage Guide

### Basic Workflow

1. **Load Files**
   - Click `📁 Open Left` or use `Ctrl+O` for left panel
   - Click `📁 Open Right` or use `Ctrl+Shift+O` for right panel
   - Files are compared automatically upon loading

2. **Edit & Compare**
   - Type directly in either panel
   - Auto-compare triggers after 500ms of inactivity
   - Toggle auto-compare with the `🔄 Auto` button

3. **Navigate Differences**
   - Use `F3` / `Shift+F3` to jump between differences
   - Click `Go` buttons in the action panel
   - Scroll to view all changes

4. **Merge Changes**
   - Click `→` to copy from left to right
   - Click `←` to copy from right to left
   - Use bulk merge for all changes at once

5. **Save Results**
   - `Ctrl+S` saves the left panel
   - `Ctrl+Shift+S` saves the right panel
   - Export differences as HTML/JSON reports

---

## ⌨️ Keyboard Shortcuts

### File Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file in left panel |
| `Ctrl+Shift+O` | Open file in right panel |
| `Ctrl+S` | Save left panel |
| `Ctrl+Shift+S` | Save right panel |

### Navigation
| Shortcut | Action |
|----------|--------|
| `F3` | Next difference |
| `Shift+F3` | Previous difference |
| `PageUp/PageDown` | Scroll panels |

### Editing
| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+F` | Find |
| `Ctrl+H` | Replace |
| `Ctrl+A` | Toggle auto-compare |

### Comparison
| Shortcut | Action |
|----------|--------|
| `F5` | Manual compare (when auto is off) |
| `Ctrl+D` | Clear all panels |

---

## ⚙️ Configuration

### Settings Dialog
Access via `Tools → Settings` to configure:
- **Auto-compare delay** - Adjust timing (100-2000ms)
- **Font size** - Text display size (8-20pt)
- **Theme preference** - Light/Dark mode
- **Sync scrolling** - Enable/disable synchronized scrolling

### Auto-Compare Settings
```python
# Default configuration
auto_compare = True          # Enable by default
compare_delay = 500          # Milliseconds
max_history = 50            # Undo/redo states
```

---

## 🎨 Themes

### Light Theme
- Clean, professional appearance
- High contrast for readability
- Ideal for well-lit environments

### Dark Theme
- Reduced eye strain
- Modern development aesthetic
- Perfect for extended use

Toggle themes via `View → Dark Mode`

---

## 📊 Export Options

### Text Report (.txt)
```
Diff Report - 2024-01-15 14:30:00
==================================
Left file: document1.txt
Right file: document2.txt
Total differences: 5

Difference #1
Type: modified
Left: Lines 10-12
Right: Lines 10-13
------------------------------
```

### HTML Report (.html)
- Styled, interactive report
- Color-coded differences
- Printable format

### JSON Export (.json)
```json
[
  {
    "type": "modified",
    "left_start": 10,
    "left_end": 12,
    "right_start": 10,
    "right_end": 13
  }
]
```

---

## 🔧 Troubleshooting

### Common Issues

**Q: Auto-compare is too sensitive/slow**
- A: Adjust the delay in Settings (Tools → Settings)

**Q: Scrolling isn't synchronized**
- A: Toggle sync scroll in View menu or with toolbar button

**Q: Can't see differences clearly**
- A: Try switching themes (View → Dark Mode)

**Q: Application is slow with large files**
- A: Disable auto-compare for files over 10,000 lines

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
```bash
# Clone repository
git clone https://github.com/JustVugg/duffydiff-pro.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

### Areas for Contribution
- 🌐 Internationalization support
- 📝 Additional file format support
- 🎨 Custom themes
- 🔌 Plugin system
- 📱 Web version

---

## 📈 Performance

- **Handles files up to 100,000 lines** efficiently
- **Memory usage**: ~50MB for typical documents
- **Comparison speed**: <100ms for 1,000 lines
- **Auto-compare overhead**: Minimal with debouncing

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 DuffyDiff Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👥 Authors

- **JustVugg** - *Initial work* - [GitHub](https://github.com/JustVugg)

### Acknowledgments
- Built with Python and Tkinter
- Inspired by popular diff tools
- Community feedback and contributions

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JustVugg/duffydiff-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JustVugg/duffydiff-pro/discussions)

---

<div align="center">

**Made with ❤️ by the DuffyDiff Team**

⭐ Star us on GitHub!

</div>
