# Vector PDF Search Pro

A professional, AI-powered semantic search tool for PDF documents. Unlike traditional keyword search, this tool understands the meaning of your queries to find the most relevant information.

## Features
- **Semantic Search**: Find content based on meaning, not just exact words.
- **Relevance Sorting**: Results are automatically ranked by accuracy.
- **Persistent Database**: Your indexed PDFs are saved locally for instant access later.
- **Cross-Platform**: Works on Windows and macOS.

---

## 1. Setup (Running from Source)

### Windows
1. Install Python 3.x from [python.org](https://www.python.org/).
2. Open PowerShell and install dependencies:
   ```powershell
   pip install chromadb sentence-transformers PyMuPDF PyQt6
   ```
3. Run the application:
   ```powershell
   python main.py
   ```

### macOS
1. macOS usually comes with Python, but it's recommended to install the latest version via [Homebrew](https://brew.sh/): `brew install python`.
2. Open Terminal and install dependencies:
   ```bash
   pip3 install chromadb sentence-transformers PyMuPDF PyQt6
   ```
3. Run the application:
   ```bash
   python3 main.py
   ```

---

## 2. Creating a Standalone App

### Windows (.exe)
1. Install PyInstaller: `pip install pyinstaller`
2. Run the build command:
   ```powershell
   pyinstaller --noconsole --onefile --name "VectorSearch" --collect-all "chromadb" --collect-all "sentence_transformers" --hidden-import "pytorch" main.py
   ```
3. Your `.exe` will be in the `dist` folder.

### macOS (.app)
1. Install PyInstaller: `pip3 install pyinstaller`
2. Run the build command:
   ```bash
   pyinstaller --noconsole --onefile --name "VectorSearch" --collect-all "chromadb" --collect-all "sentence_transformers" --hidden-import "pytorch" main.py
   ```
3. Your `.app` bundle will be in the `dist` folder.
   *Note: On macOS, you may need to grant the app permission in "System Settings > Privacy & Security" the first time you run it.*

---

## Project Structure
- `main.py`: The core application code.
- `sample.pdf`: A 10-page test document.
- `requirements.txt`: List of necessary Python libraries.
- `.gitignore`: Rules for excluding temporary files.
