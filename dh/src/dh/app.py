import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QTextCursor
from mlx_lm import load, stream_generate  # Ensure this package is installed

# Worker thread to stream AI responses without blocking the UI.
class ChatWorker(QThread):
    token_received = Signal(str)
    finished_signal = Signal()

    def __init__(self, model, tokenizer, user_message: str):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.user_message = user_message

    def run(self):
        # Prepare the prompt using the chat template.
        messages = [{"role": "user", "content": self.user_message}]
        prompt = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        try:
            for response in stream_generate(self.model, self.tokenizer, prompt, max_tokens=512):
                # Emit each token as it's received.
                self.token_received.emit(response.text)
        except Exception as e:
            self.token_received.emit(f"\n[Error during generation: {e}]")
        self.finished_signal.emit()

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Model Chat")
        self.setGeometry(100, 100, 600, 500)
        self.model = None
        self.tokenizer = None
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Top layout for model selection.
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "mlx-community/gemma-3-4b-pt-4bit",
            "mlx-community/phi-4-abliterated-3bit"
        ])
        self.model_combo.setEditable(False)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Or enter model ID here")
        self.load_button = QPushButton("Load Model")
        self.load_button.clicked.connect(self.load_model)

        model_layout.addWidget(QLabel("Select Model:"))
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(QLabel("Or:"))
        model_layout.addWidget(self.model_input)
        model_layout.addWidget(self.load_button)
        main_layout.addLayout(model_layout)

        # Chat display area.
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        # Bottom layout for user input.
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type your message here...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        central_widget.setLayout(main_layout)

    def apply_styles(self):
        # Apply CSS styles including a gradient background.
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff9a9e, stop:1 #fad0c4);
            }
            QTextEdit, QLineEdit, QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 14px;
                padding: 5px 10px;
                background-color: #6a11cb;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2575fc;
            }
        """)

    def load_model(self):
        # Determine the model ID from the input or the combo box.
        model_id = self.model_input.text().strip() or self.model_combo.currentText()
        try:
            self.model, self.tokenizer = load(model_id)
            QMessageBox.information(self, "Model Loaded", f"Model '{model_id}' loaded successfully!")
            self.chat_display.append(f"<i>Loaded model: {model_id}</i>")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load model: {e}")

    def send_message(self):
        if self.model is None or self.tokenizer is None:
            QMessageBox.warning(self, "No Model", "Please load a model first.")
            return

        user_text = self.input_line.text().strip()
        if not user_text:
            return

        # Append the user's message. QTextEdit.append() creates a new block automatically.
        self.chat_display.append(f"<b>User:</b> {user_text}")
        self.input_line.clear()

        # Insert a new block and then the "Model:" label.
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()
        cursor.insertHtml("<b>Model:</b> ")
        self.chat_display.setTextCursor(cursor)

        self.send_button.setEnabled(False)

        # Start the worker thread to stream the model response.
        self.worker = ChatWorker(self.model, self.tokenizer, user_text)
        self.worker.token_received.connect(self.append_token)
        self.worker.finished_signal.connect(self.worker_finished)
        self.worker.start()

    def append_token(self, token: str):
        # Append each token directly to the current text block.
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(token)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def worker_finished(self):
        self.send_button.setEnabled(True)
        # Optionally, insert a newline after the complete response.
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()
        self.chat_display.setTextCursor(cursor)
def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
