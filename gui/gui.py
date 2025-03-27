from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QTextBrowser
from backend import get_response_from_model  

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Dumbass gui v1')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        layout.addWidget(self.prompt_input)

        self.submit_button = QPushButton('Get Response', self)
        self.submit_button.clicked.connect(self.on_button_click)
        layout.addWidget(self.submit_button)

        self.response_browser = QTextBrowser(self)
        layout.addWidget(self.response_browser)

        self.setLayout(layout)

    def on_button_click(self):
        prompt = self.prompt_input.text()

        if prompt:
            response = get_response_from_model(prompt)
            self.response_browser.setText(response)
        else:
            self.response_browser.setText("Please enter a prompt.")
