import sys
import os
import json
import requests
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QLineEdit, QTextBrowser, QFileDialog, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:8321/generate")
MODEL_ID = os.getenv("INFERENCE_MODEL", "llama3.2:1b-instruct-fp16")

class ModelRequestThread(QThread):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        payload = {"prompt": self.prompt}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(OLLAMA_URL, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                self.response_received.emit(response_json.get("response", "No response found"))
            else:
                self.error_occurred.emit(f"Error {response.status_code}: {response.text}")
        except requests.RequestException as e:
            self.error_occurred.emit(f"Error: {str(e)}")

class AIFileExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AI-Powered File Explorer")
        self.setGeometry(100, 100, 700, 500)
        
        layout = QVBoxLayout()

        # Folder Selection UI
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)
        
        # Prompt Input
        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        layout.addWidget(self.prompt_input)
        
        # Submit Button
        self.submit_button = QPushButton("Get Response", self)
        self.submit_button.clicked.connect(self.on_button_click)
        layout.addWidget(self.submit_button)
        
        # Response Output
        self.response_browser = QTextBrowser(self)
        layout.addWidget(self.response_browser)
        
        self.setLayout(layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder_path:
            self.folder_label.setText(os.path.basename(folder_path))
            logging.info(f"Folder selected: {folder_path}")

    def on_button_click(self):
        prompt = self.prompt_input.text().strip()

        if not prompt:
            QMessageBox.warning(self, "Input Error", "Please enter a prompt.")
            return

        self.submit_button.setEnabled(False)
        self.response_browser.setText("Processing...")

        self.thread = ModelRequestThread(prompt)
        self.thread.response_received.connect(self.display_response)
        self.thread.error_occurred.connect(self.display_error)
        self.thread.start()

    def display_response(self, response):
        self.response_browser.setText(response)
        self.submit_button.setEnabled(True)

    def display_error(self, error):
        QMessageBox.critical(self, "Error", error)
        self.response_browser.setText("An error occurred.")
        self.submit_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AIFileExplorer()
    window.show()
    sys.exit(app.exec_())
