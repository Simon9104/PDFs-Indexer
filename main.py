import sys
import os
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QFileDialog, QLabel,
    QProgressBar, QMessageBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Use a lightweight embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class VectorIndexThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, directory, collection):
        super().__init__()
        self.directory = os.path.abspath(directory)
        self.collection = collection
        self.is_running = True

    def run(self):
        try:
            pdf_files = [f for f in os.listdir(self.directory) if f.lower().endswith('.pdf')]
            total_files = len(pdf_files)
            
            if total_files == 0:
                self.finished.emit()
                return

            for i, filename in enumerate(pdf_files):
                if not self.is_running:
                    break
                
                self.status.emit(f"Indexing: {filename}")
                file_path = os.path.join(self.directory, filename)
                
                try:
                    doc = fitz.open(file_path)
                    for page_num in range(len(doc)):
                        if not self.is_running:
                            break
                        page = doc.load_page(page_num)
                        text = page.get_text().strip()
                        
                        if text:
                            self.collection.add(
                                documents=[text],
                                metadatas=[{"filename": filename, "page": page_num + 1}],
                                ids=[f"{filename}_p{page_num}"]
                            )
                    doc.close()
                except Exception as e:
                    print(f"Error indexing {filename}: {e}")
                
                self.progress.emit(int((i + 1) / total_files * 100))
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class VectorSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Vector PDF Search")
        self.setMinimumSize(700, 500)
        
        # Initialize ChromaDB
        db_path = os.path.join(os.path.expanduser("~"), "vector_search_db_simple")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        self.collection = self.chroma_client.get_or_create_collection(
            name="pdf_collection", 
            embedding_function=self.emb_fn
        )
        
        self.last_results = []
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Step 1: Directory
        layout.addWidget(QLabel("<b>1. Select Folder</b>"))
        dir_layout = QHBoxLayout()
        self.dir_label = QLineEdit()
        self.dir_label.setPlaceholderText("Select directory...")
        self.dir_label.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        self.index_btn = QPushButton("Index")
        self.index_btn.clicked.connect(self.start_indexing)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(browse_btn)
        dir_layout.addWidget(self.index_btn)
        layout.addLayout(dir_layout)

        # Step 2: Search
        layout.addWidget(QLabel("<b>2. Search</b>"))
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter your question...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # Sorting & Options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Sort by:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Relevance (High to Low)", "Relevance (Low to High)", "Page Number", "Filename"])
        self.sort_combo.currentIndexChanged.connect(self.display_results)
        
        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(1, 50)
        self.top_k_spin.setValue(10)
        self.top_k_spin.setPrefix("Show top ")
        
        options_layout.addWidget(self.sort_combo)
        options_layout.addStretch()
        options_layout.addWidget(self.top_k_spin)
        layout.addLayout(options_layout)

        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Results
        layout.addWidget(QLabel("<b>3. Results</b> (Double-click to open)"))
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_pdf)
        layout.addWidget(self.results_list)

        self.index_thread = None

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_label.setText(directory)

    def start_indexing(self):
        directory = self.dir_label.text()
        if not directory or not os.path.isdir(directory):
            QMessageBox.warning(self, "Error", "Please select a valid directory.")
            return

        try:
            self.chroma_client.delete_collection("pdf_collection")
        except:
            pass
        self.collection = self.chroma_client.create_collection(
            name="pdf_collection", 
            embedding_function=self.emb_fn
        )

        self.index_btn.setEnabled(False)
        self.search_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.index_thread = VectorIndexThread(directory, self.collection)
        self.index_thread.progress.connect(self.progress_bar.setValue)
        self.index_thread.status.connect(self.status_label.setText)
        self.index_thread.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.index_thread.finished.connect(self.indexing_finished)
        self.index_thread.start()

    def indexing_finished(self):
        self.index_btn.setEnabled(True)
        self.search_btn.setEnabled(True)
        self.status_label.setText("Indexing complete.")
        QMessageBox.information(self, "Success", "Done!")

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.status_label.setText("Searching...")
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=self.top_k_spin.value()
            )
            
            self.last_results = []
            if results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    self.last_results.append({
                        'text': results['documents'][0][i],
                        'filename': results['metadatas'][0][i]['filename'],
                        'page': results['metadatas'][0][i]['page'],
                        'distance': results['distances'][0][i],
                        'score': max(0, 1 - results['distances'][0][i])
                    })
            
            self.display_results()
            self.status_label.setText(f"Found {len(self.last_results)} matches.")
        except Exception as e:
            QMessageBox.critical(self, "Search Error", str(e))

    def display_results(self):
        self.results_list.clear()
        if not self.last_results:
            return

        # Sorting logic
        sort_type = self.sort_combo.currentText()
        if sort_type == "Relevance (High to Low)":
            sorted_data = sorted(self.last_results, key=lambda x: x['score'], reverse=True)
        elif sort_type == "Relevance (Low to High)":
            sorted_data = sorted(self.last_results, key=lambda x: x['score'])
        elif sort_type == "Page Number":
            sorted_data = sorted(self.last_results, key=lambda x: (x['filename'], x['page']))
        elif sort_type == "Filename":
            sorted_data = sorted(self.last_results, key=lambda x: x['filename'])
        else:
            sorted_data = self.last_results

        for item in sorted_data:
            display_text = f"[{item['score']:.1%}] {item['filename']} (Page {item['page']})\n"
            display_text += f"{item['text'][:120]}..."
            self.results_list.addItem(display_text)

    def open_pdf(self, item):
        try:
            # Extract filename from the first line of the item text
            header = item.text().split('\n')[0]
            # Format is "[95.0%] filename.pdf (Page 1)"
            filename = header.split('] ')[1].split(' (Page')[0].strip()
            file_path = os.path.join(self.dir_label.text(), filename)
            
            if os.path.exists(file_path):
                if sys.platform == 'win32':
                    os.startfile(file_path)
                else:
                    import subprocess
                    cmd = 'open' if sys.platform == 'darwin' else 'xdg-open'
                    subprocess.call([cmd, file_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorSearchApp()
    window.show()
    sys.exit(app.exec())
