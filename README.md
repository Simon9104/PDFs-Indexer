# Vector PDF Search Pro

A professional, AI-powered semantic search tool for PDF documents. Unlike traditional keyword search, this tool understands the meaning of your queries to find the most relevant information.

## Features
- **Semantic Search**: Find content based on meaning, not just exact words.
- **Relevance Sorting**: Results are automatically ranked by accuracy.
- **Persistent Database**: Your indexed PDFs are saved locally for instant access later.
- **Minimalist UI**: A clean, easy-to-use interface designed for Windows.

## Quick Start (Running from Source)
1. Install Python 3.x.
2. Install dependencies:
   ```powershell
   pip install chromadb sentence-transformers PyMuPDF PyQt6
   ```
3. Run the application:
   ```powershell
   python main.py
   ```

## How to Create a Standalone .exe
To create a single executable file for Windows:
1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Run the build command:
   ```powershell
   pyinstaller --noconsole --onefile --name "VectorSearch" --collect-all "chromadb" --collect-all "sentence_transformers" --hidden-import "pytorch" main.py
   ```
3. Your `.exe` will be in the `dist` folder.

## Project Structure
- `main.py`: The core application code.
- `sample.pdf`: A 10-page test document.
- `requirements.txt`: List of necessary Python libraries.
- `.gitignore`: Rules for excluding temporary files from version control.
