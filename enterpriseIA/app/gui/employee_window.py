# employee_window.py
import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QLineEdit, QFileDialog, QMessageBox,
    QDockWidget, QListWidget, QListWidgetItem, QToolBar, QSizePolicy, QFrame
)
from PySide6.QtGui import QIcon, QTextCursor, QFont, QPalette, QColor, QLinearGradient
from PySide6.QtCore import Qt, QSize

# Import the real System from your backend.
from ..system import System

class EmployeeChatDashboard(QMainWindow):
    def __init__(self, system, user=None):
        super().__init__()
        self.system = system
        if user:
            self.employee_user = user
        else:
            # Import your real Employee model as needed
            from ..models.employee import Employee
            self.employee_user = Employee(user_id=2, username="employee", hashed_password="", fullname="Employee")
        
        self.setWindowTitle("Employee IA Chat Dashboard")
        self.setGeometry(100, 100, 900, 650)
        self.setMinimumSize(700, 500)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)
        
        self.apply_enhanced_theme()
        
        self.create_chat_history_dock()
        self.create_chat_history_toggle_toolbar()
        self.create_profile_toolbar()
        
        self.init_ui()
    
    def apply_enhanced_theme(self):
        palette = QPalette()
        background_gradient = QLinearGradient(0, 0, 0, 1)
        background_gradient.setColorAt(0.0, QColor("#2C3E50"))
        background_gradient.setColorAt(1.0, QColor("#34495E"))
        palette.setBrush(QPalette.Window, background_gradient)
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor("#1F2A37"))
        palette.setColor(QPalette.AlternateBase, QColor("#2C3E50"))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor("#16A085"))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor("#1ABC9C"))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C3E50,
                    stop:1 #34495E
                );
                font-family: 'Helvetica';
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #16A085;
                color: #ECF0F1;
                border: none;
                padding: 10px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1ABC9C;
                color: #2C3E50;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1F2A37;
                color: #ECF0F1;
                border: 1px solid #16A085;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #1ABC9C;
            }
            QTextEdit {
                font-size: 12px;
            }
            QGroupBox {
                border: 2px solid #16A085;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #ECF0F1;
                font-size: 16px;
                font-weight: bold;
            }
            QToolBar {
                background: transparent;
                border: none;
            }
            QListWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: none;
            }
        """)
    
    def create_chat_history_dock(self):
        self.chat_history_dock = QDockWidget("Chat History", self)
        self.chat_history_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.chat_history_list = QListWidget()
        self.chat_history_list.setStyleSheet("""
            QListWidget::item {
                background-color: #1F2A37;
                padding: 8px;
                margin: 4px 0;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #16A085;
                color: #2C3E50;
            }
        """)
        self.chat_history_dock.setWidget(self.chat_history_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.chat_history_dock)
        self.chat_history_dock.hide()
    
    def create_chat_history_toggle_toolbar(self):
        toolbar = QToolBar("Chat History")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.setIconSize(QSize(30, 30))
        chat_history_btn = QPushButton()
        history_icon = QIcon("icons/history_icon.png")
        chat_history_btn.setIcon(history_icon)
        chat_history_btn.setFixedSize(35, 35)
        chat_history_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 5px;
                background-color: #16A085;
            }
            QPushButton:hover {
                background-color: #1ABC9C;
            }
        """)
        chat_history_btn.clicked.connect(self.toggle_chat_history)
        toolbar.addWidget(chat_history_btn)
    
    def toggle_chat_history(self):
        if self.chat_history_dock.isVisible():
            self.chat_history_dock.hide()
        else:
            self.chat_history_dock.show()
            self.chat_history_dock.setFloating(False)
    
    def create_profile_toolbar(self):
        toolbar = QToolBar("Profile")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.setIconSize(QSize(40, 40))
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        profile_btn = QPushButton()
        profile_icon = QIcon(".icons/profile_icon.png")
        profile_btn.setIcon(profile_icon)
        profile_btn.setFixedSize(40, 40)
        profile_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 20px;
                background-color: #16A085;
            }
            QPushButton:hover {
                background-color: #1ABC9C;
            }
        """)
        profile_btn.clicked.connect(self.show_profile)
        toolbar.addWidget(profile_btn)
    
    def show_profile(self):
        QMessageBox.information(
            self, "Profile",
            f"User: {self.employee_user.username}\nFull Name: {self.employee_user.fullname}"
        )
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header Frame with a gradient background
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16A085,
                    stop:1 #1ABC9C
                );
                border-radius: 6px;
                margin: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Employee IA Chat Interface")
        title_label.setFont(QFont("Helvetica", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Conditionally add a switch button based on user type.
        if type(self.employee_user).__name__ == "Admin":
            switch_button = QPushButton("Go to Admin Dashboard")
            switch_button.clicked.connect(self.go_to_admin)
            header_layout.addWidget(switch_button)
        elif type(self.employee_user).__name__ == "DPO":
            switch_button = QPushButton("Go to DPO Dashboard")
            switch_button.clicked.connect(self.go_to_dpo)
            header_layout.addWidget(switch_button)
        # If a simple employee, no switch button is added.
        
        main_layout.addWidget(header_frame)
        
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
        self.chat_display.setFont(QFont("Helvetica", 10))
        self.chat_display.setStyleSheet("""
            background-color: #1F2A37;
            border: 1px solid #16A085;
            border-radius: 5px;
            padding: 8px;
        """)
        main_layout.addWidget(self.chat_display)
        
        # Message entry layout
        message_frame = QHBoxLayout()
        attach_btn = QPushButton()
        attach_icon = QIcon("icons/upload_icon.png")
        attach_btn.setIcon(attach_icon)
        attach_btn.setFixedSize(35, 35)
        attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #16A085;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1ABC9C;
            }
        """)
        attach_btn.setToolTip("Attach File")
        attach_btn.clicked.connect(self.upload_file)
        message_frame.addWidget(attach_btn, 0)
        
        self.message_entry = QLineEdit()
        self.message_entry.setPlaceholderText("Type your message here...")
        self.message_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.message_entry.returnPressed.connect(self.send_message)
        message_frame.addWidget(self.message_entry, 1)
        
        send_btn = QPushButton("Send")
        send_btn.setFixedHeight(35)
        send_btn.clicked.connect(self.send_message)
        message_frame.addWidget(send_btn, 0)
        main_layout.addLayout(message_frame)
        
        self.append_chat_message("System", "Welcome! How can I assist you today?")
    
    def go_to_admin(self):
        from admin_window import AdminDashboard
        dashboard = AdminDashboard(system=self.system, admin_user=self.employee_user)
        dashboard.show()
        self.close()
    
    def go_to_dpo(self):
        from dpo_window import DPODashboard
        dashboard = DPODashboard(system=self.system, current_user=self.employee_user)
        dashboard.show()
        self.close()
    
    def append_chat_message(self, sender: str, message: str):
        self.chat_display.setReadOnly(False)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        if sender == "System":
            cursor.insertHtml(f"""
                <div style="background-color: #2C3E50; 
                            border-radius: 8px; 
                            padding: 8px; 
                            margin-bottom: 10px;">
                    <span style="color: #1ABC9C; font-weight: bold;">{sender}:</span>
                    <span style="color: #ECF0F1;">{message}</span>
                </div>
            """)
        elif sender == "You":
            cursor.insertHtml(f"""
                <div style="background-color: #4A4A4A;
                            color: #ECF0F1;
                            padding: 8px;
                            border-radius: 8px;
                            max-width: 60%;
                            margin: 5px 0 10px auto;">
                    <b>{sender}:</b> {message}
                </div>
            """)
        else:
            cursor.insertHtml(f"""
                <div style="background-color: #3D3D3D;
                            border-radius: 8px;
                            padding: 8px;
                            margin-bottom: 10px;">
                    <b style="color: #1ABC9C;">{sender}:</b>
                    <span style="color: #ECF0F1;">{message}</span>
                </div>
            """)
        self.chat_display.setReadOnly(True)
        self.chat_display.moveCursor(QTextCursor.End)
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
            response_obj = self.system.makeRequest(
                self.employee_user, query, use_external_ai=False
            )
            self.append_chat_message("Internal IA (Mistral)", response_obj.content)
        elif ia_service == "External IA (OpenAI)":
            response_obj = self.system.makeRequest(
                self.employee_user, query, use_external_ai=True
            )
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

def main():
    system = System(external_api_key="initial_api_key_12345")
    # For testing, you can pass a dummy Admin or DPO user.
    # Example:
    # from ..models.admin import Admin
    # user = Admin(user_id=1, username="admin", hashed_password="", fullname="Administrator")
    # from ..models.dpo import DPO
    # user = DPO(user_id=3, username="dpo", hashed_password="", fullname="Data Protection Officer")
    # For a simple employee, leave user as None.
    user = None
    app = QApplication(sys.argv)
    dashboard = EmployeeChatDashboard(system=system, user=user)
    dashboard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
