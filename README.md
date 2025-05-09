# Entropy Analyzer

**Entropy Analyzer** is a Python-based GUI tool for analyzing the entropy of files using a sliding window and visualizing the results interactively. It can help identify encrypted, compressed, or structured regions within files based on byte-level Shannon entropy.

## Features

- Shannon entropy calculation with sliding windows
- Interactive graph with zoom and pan
- Multiple file analysis at once
- Color-coded entropy bands for easy interpretation
- English and Hungarian language support
- Built-in user guide (localized)
- Export graphs as PNG or SVG

## Installation

1. Clone or download the repository.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the program:
   ```bash
   python "entropy analyzer.py"
   ```

## Usage

1. Select a folder with files to analyze.
2. Choose one or more files from the list.
3. Set the sliding window size (in bytes).
4. Click **Load Files** to analyze and plot entropy.
5. Use the graph interactively or export the results.

The built-in Help window provides more detailed usage instructions and background information.

## Dependencies

- Python 3.6+
- numpy
- matplotlib
- tkinter (usually included with Python)

## License

This project is open source and free to use or modify.

## Other Languages

- [Magyar (Hungarian) README](README_HU.md)
