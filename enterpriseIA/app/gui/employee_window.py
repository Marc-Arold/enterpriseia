import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QLineEdit, QFileDialog, QMessageBox,
    QDockWidget, QListWidget, QListWidgetItem, QToolBar, QSizePolicy
)
from PySide6.QtGui import QIcon, QTextCursor, QFont, QPalette, QColor
from PySide6.QtCore import Qt, QSize

# Import the real System from your backend.
from ..system import System

class EmployeeChatDashboard(QMainWindow):
    def __init__(self, system):
        super().__init__()
        self.system = system
        
        # Create a dummy employee user for queries.
        from ..models.employee import Employee
        self.employee_user = Employee(user_id=2, username="employee", hashed_password="", fullname="Employee")
        
        self.setWindowTitle("Employee IA Chat Dashboard")
        self.setGeometry(100, 100, 900, 650)
        self.setMinimumSize(700, 500)
        # Enable animated docks and nested docking to smoothly adjust the interface.
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)
        
        # Apply dark theme and custom styles.
        self.apply_dark_theme()
        
        # Create the chat history dock BEFORE initializing the main UI.
        self.create_chat_history_dock()
        # Create a toolbar with a toggle button to show/hide chat history.
        self.create_chat_history_toggle_toolbar()
        # Create the profile toolbar on the top-right.
        self.create_profile_toolbar()
        
        # Setup main UI.
        self.init_ui()
    
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)
        self.setStyleSheet("""
            QMainWindow { background-color: #2C3E50; }
            QLabel { color: #ECF0F1; font-size: 14px; }
            QPushButton { 
                background-color: #1ABC9C; 
                color: #2C3E50; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { background-color: #16A085; color: #ECF0F1; }
            QLineEdit, QTextEdit, QComboBox { 
                background-color: #34495E; 
                color: #ECF0F1; 
                border: 1px solid #1ABC9C; 
                border-radius: 5px; 
                padding: 5px; 
                font-size: 14px; 
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #1ABC9C; }
            QTextEdit { font-size: 12px; }
            QGroupBox { border: 2px solid #1ABC9C; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 5px; 
                color: #ECF0F1; 
                font-size: 16px; 
                font-weight: bold; 
            }
        """)

    def create_chat_history_dock(self):
        """
        Create a dockable sidebar to display chat history.
        """
        self.chat_history_dock = QDockWidget("Chat History", self)
        self.chat_history_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.chat_history_list = QListWidget()
        self.chat_history_dock.setWidget(self.chat_history_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.chat_history_dock)
        self.chat_history_dock.hide()  # Start hidden

    def create_chat_history_toggle_toolbar(self):
        """
        Create a toolbar with a toggle button to show/hide chat history.
        """
        toolbar = QToolBar("Chat History")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setStyleSheet("QToolBar { background: transparent; border: none; }")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.setIconSize(QSize(30, 30))
        
        chat_history_btn = QPushButton()
        history_icon = QIcon("icons/history_icon.png")  # Ensure this icon exists
        chat_history_btn.setIcon(history_icon)
        chat_history_btn.setFixedSize(30, 30)
        chat_history_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #1ABC9C;
                border-radius: 15px;
            }
            QPushButton:hover { background-color: #16A085; }
        """)
        chat_history_btn.clicked.connect(self.toggle_chat_history)
        toolbar.addWidget(chat_history_btn)
    
    def toggle_chat_history(self):
        """
        Toggle the visibility of the chat history sidebar and ensure it docks.
        """
        if self.chat_history_dock.isVisible():
            self.chat_history_dock.hide()
        else:
            self.chat_history_dock.show()
            self.chat_history_dock.setFloating(False)
    
    def create_profile_toolbar(self):
        """
        Add a toolbar at the top-right with a round profile icon.
        """
        toolbar = QToolBar("Profile")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setStyleSheet("QToolBar { background: transparent; border: none; }")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.setIconSize(QSize(40, 40))
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        profile_btn = QPushButton()
        profile_icon = QIcon("icons/profile_icon.png")  # Use a circular image for profile
        profile_btn.setIcon(profile_icon)
        profile_btn.setFixedSize(40, 40)
        profile_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 20px;
                background-color: #1ABC9C;
            }
            QPushButton:hover { background-color: #16A085; }
        """)
        profile_btn.clicked.connect(self.show_profile)
        toolbar.addWidget(profile_btn)
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        title_label = QLabel("Employee IA Chat Interface")
        title_label.setFont(QFont("Helvetica", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # IA Service Selection Frame
        ia_frame = QHBoxLayout()
        ia_label = QLabel("Select IA Service:")
        ia_label.setFont(QFont("Helvetica", 12))
        ia_frame.addWidget(ia_label)
        
        self.ia_service_combo = QComboBox()
        self.ia_service_combo.addItems(["Internal IA (Mistral)", "External IA (OpenAI)"])
        self.ia_service_combo.setCurrentText("Internal IA (Mistral)")
        ia_frame.addWidget(self.ia_service_combo)
        ia_frame.addStretch()
        main_layout.addLayout(ia_frame)
        
        # Chat Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #34495E;")
        self.chat_display.setFont(QFont("Helvetica", 10))
        main_layout.addWidget(self.chat_display)
        
        # Combined Message Entry Frame with Attach on Left, Input in Middle, and Send on Right.
        message_frame = QHBoxLayout()
        
        # Attach Button (Left)
        attach_btn = QPushButton()
        attach_icon = QIcon("icons/upload_icon.png")  # Ensure this icon exists
        attach_btn.setIcon(attach_icon)
        attach_btn.setFixedSize(30, 30)
        attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #1ABC9C;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #16A085; }
        """)
        attach_btn.setToolTip("Attach File")
        attach_btn.clicked.connect(self.upload_file)
        message_frame.addWidget(attach_btn, 0)
        
        # Message Input Field (Middle)
        self.message_entry = QLineEdit()
        self.message_entry.setPlaceholderText("Type your message here...")
        self.message_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.message_entry.returnPressed.connect(self.send_message)
        message_frame.addWidget(self.message_entry, 1)
        
        # Send Button (Right)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        message_frame.addWidget(send_btn, 0)
        
        main_layout.addLayout(message_frame)
        
        self.append_chat_message("System", "Welcome! How can I assist you today?")
    
    def show_profile(self):
        QMessageBox.information(self, "Profile", f"User: {self.employee_user.username}\nFull Name: {self.employee_user.fullname}")
    
    def append_chat_message(self, sender: str, message: str):
        self.chat_display.setReadOnly(False)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if sender == "System":
            self.chat_display.setTextColor(QColor("blue"))
            self.chat_display.setFontWeight(QFont.Bold)
            cursor.insertText(f"{sender}: {message}\n")
        elif sender == "You":
            self.chat_display.setTextColor(QColor("white"))
            self.chat_display.setFontWeight(QFont.Normal)
            cursor.insertHtml(f'''
                <div style="background-color: #4A4A4A; padding:5px; border-radius:5px; max-width: 60%; margin: 5px;">
                    <b>You:</b> {message}
                </div>
                <br>
            ''')
        else:
            self.chat_display.setTextColor(QColor("purple"))
            self.chat_display.setFontWeight(QFont.Normal)
            cursor.insertText(f"{sender}: {message}\n")
        
        self.chat_display.setReadOnly(True)
        self.chat_display.moveCursor(QTextCursor.End)
        
        # Also add the message to the chat history list if available.
        if hasattr(self, 'chat_history_list'):
            item = QListWidgetItem(f"{sender}: {message}")
            self.chat_history_list.addItem(item)
    
    def send_message(self, event=None):
        query = self.message_entry.text().strip()
        if not query:
            return
        
        self.append_chat_message("You", query)
        self.message_entry.clear()
        
        ia_service = self.ia_service_combo.currentText()
        if ia_service == "Internal IA (Mistral)":
            response_obj = self.system.makeRequest(self.employee_user, query, use_external_ai=False)
            self.append_chat_message("Internal IA (Mistral)", response_obj.content)
        elif ia_service == "External IA (OpenAI)":
            response_obj = self.system.makeRequest(self.employee_user, query, use_external_ai=True)
            self.append_chat_message("External IA (OpenAI)", response_obj.content)
        else:
            self.append_chat_message("System", "❌ Invalid IA service selected.")
    
    def upload_file(self):
        ia_service = self.ia_service_combo.currentText()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Upload",
            "",
            "All Files (*.*)"
        )
        if not file_path:
            return
        
        self.append_chat_message("System", f"Uploading '{os.path.basename(file_path)}' to {ia_service}...")
        result = self.system.upload_file_to_ia(ia_type=ia_service, file_path=file_path)
        self.append_chat_message("System", result)

# --------------------------- Main Application ---------------------------
def main():
    system = System(external_api_key="initial_api_key_12345")
    app = QApplication(sys.argv)
    dashboard = EmployeeChatDashboard(system=system)
    dashboard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
