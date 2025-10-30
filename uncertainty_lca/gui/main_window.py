from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from uncertainty_lca.config.settings import Settings

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Uncertainty LCA GUI")

        self.settings = Settings("config.ini")

        self.layout = QVBoxLayout()

        # Example input field
        self.input_label = QLabel("Enter your project name:")
        self.input_field = QLineEdit()
        self.input_field.setText(self.settings.get("user_input", ""))  # Load previous input

        self.save_button = QPushButton("Save Input")
        self.save_button.clicked.connect(self.save_input)

        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_input(self):
        text = self.input_field.text()
        self.settings.set("user_input", text)
