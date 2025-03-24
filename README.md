DuffyDiff is a modern, user-friendly text comparison tool built with Python and Tkinter. It allows users to easily compare two text files, navigate between differences, and merge content between files.

Features
Clean, modern UI with intuitive controls
Side-by-side text comparison with syntax highlighting
Line numbering for easy reference
Quick navigation between differences
Merge capabilities in both directions
Undo functionality for edits
File loading and saving
Keyboard shortcuts for common operations
Installation
Prerequisites
Python 3.6 or higher
Tkinter (usually comes bundled with Python)
Setup
Clone this repository:

git clone https://github.com/yourusername/duffydiff.git
cd duffydiff
Run the application:

python duffydiff.py
Usage
Loading Files:
Click "Load Left" or "Load Right" to choose files for comparison
You can also manually enter text in either panel
Comparing:
Click the "Compare" button to analyze differences between the two texts
Navigating Differences:
Use "Previous" and "Next" buttons to jump between differences
Differences are highlighted with color-coding:
Green: Added content
Red: Removed content
Merging:
Use the merge controls in the center panel to merge specific differences
"Merge All to Left/Right" buttons to merge everything at once
Saving:
Click "Save File" to save either the left or right panel content
Keyboard Shortcuts:
Ctrl+Z: Undo
Ctrl+N: Next difference
Ctrl+P: Previous difference
Ctrl+S: Save file
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
