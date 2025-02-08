import sys
import os
import json
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QFileDialog,
    QMessageBox, QDockWidget, QListWidget, QListWidgetItem, QToolBar,
    QSizePolicy, QFrame, QInputDialog, QScrollArea, QStatusBar
)
from PySide6.QtGui import (
    QIcon, QPalette, QColor, QAction, QKeySequence, QGuiApplication, QFont
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QSettings, QTimer, QDateTime
)

from ..system import System

# =============================================================================
# Reusable Components
# =============================================================================
class ChatMessageWidget(QWidget):
    """Custom widget for displaying chat messages with metadata."""
    
    def __init__(self, sender: str, message: str, timestamp: QDateTime, 
                 is_error: bool = False, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(4)
        
        header = QHBoxLayout()
        self.sender_label = QLabel(sender)
        self.sender_label.setStyleSheet("font-weight: bold; font-size: 12px; background-color: transparent;")
        self.time_label = QLabel(timestamp.toString("hh:mm AP"))
        self.time_label.setStyleSheet("font-size: 10px; background-color: transparent;")
        header.addWidget(self.sender_label)
        header.addStretch()
        header.addWidget(self.time_label)
        
        self.content = QLabel(message)
        self.content.setWordWrap(True)
        self.content.setStyleSheet("background-color: transparent;")
        
        self.layout.addLayout(header)
        self.layout.addWidget(self.content)
        
        self._apply_message_style(is_error)

    def _apply_message_style(self, is_error: bool):
        if is_error:
            bg_color = "#F8D7DA"
            text_color = "#721C24"
            border_color = "#F5C6CB"
        else:
            bg_color = "#2C3E50"
            text_color = "#ECF0F1"
            border_color = "#16A085"
            
        self.setStyleSheet(f"""
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
        """)
        self.content.setStyleSheet(f"background-color: transparent; color: {text_color}; padding: 8px;")
        self.sender_label.setStyleSheet(f"background-color: transparent; color: {text_color}; font-weight: bold; font-size: 12px;")
        self.time_label.setStyleSheet(f"background-color: transparent; color: {text_color}; font-size: 10px;")

# =============================================================================
# Background Worker
# =============================================================================
class AIWorker(QThread):
    """Background worker for handling AI requests."""
    response_received = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, system: System, user, query: str, use_external: bool):
        super().__init__()
        self.system = system
        self.user = user
        self.query = query
        self.use_external = use_external

    def run(self):
        try:
            response = self.system.makeRequest(
                self.user,
                self.query,
                use_external_ai=self.use_external
            )
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

# =============================================================================
# Main Window Implementation
# =============================================================================
class EmployeeChatDashboard(QMainWindow):
    def __init__(self, system: System, user=None):
        super().__init__()
        self.system = system
        self.user = user or self._create_default_user()
        self._current_worker: Optional[AIWorker] = None
        self._typing_indicator_active = False
        self._message_history = []
        self._dark_theme = True

        self.ellipsis_count = 0
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self._update_typing_indicator)

        self._configure_window()
        self._create_actions()
        self._create_ui()
        self._apply_theme()
        self._load_settings()
        self._setup_shortcuts()

    # =========================================================================
    # Configuration Methods
    # =========================================================================
    def _configure_window(self):
        self.setWindowTitle("Employee AI Chat Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)

    def _create_actions(self):
        self.export_action = QAction("Export Chat", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.triggered.connect(self._export_chat)

        self.search_action = QAction("Search History", self)
        self.search_action.setShortcut(QKeySequence.Find)
        self.search_action.triggered.connect(self._show_search)

        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        self.toggle_theme_action.triggered.connect(self._toggle_theme)

    def _setup_shortcuts(self):
        self.addAction(self.export_action)
        self.addAction(self.search_action)
        self.addAction(self.toggle_theme_action)

    # =========================================================================
    # UI Components
    # =========================================================================
    def _create_ui(self):
        self._create_toolbars()
        self._create_chat_history_dock()
        self._create_main_interface()
        self._create_status_bar()

    def _create_toolbars(self):
        main_toolbar = QToolBar("Main Tools")
        main_toolbar.setObjectName("MainToolbar")
        main_toolbar.setMovable(False)
        if main_toolbar.layout():
            main_toolbar.layout().setSpacing(10)
        self.addToolBar(Qt.TopToolBarArea, main_toolbar)
        
        self.history_btn = QPushButton()
        self.history_btn.setIcon(self._get_icon("history_icon"))
        self.history_btn.clicked.connect(self.toggle_chat_history)
        main_toolbar.addWidget(self.history_btn)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main_toolbar.addWidget(spacer)
        
        self.theme_btn = QPushButton()
        self.theme_btn.setIcon(self._get_icon("theme_icon"))
        self.theme_btn.clicked.connect(self._toggle_theme)
        main_toolbar.addWidget(self.theme_btn)
        
        fixed_spacer = QWidget()
        fixed_spacer.setFixedWidth(20)
        main_toolbar.addWidget(fixed_spacer)
        
        self.share_btn = QPushButton()
        self.share_btn.setIcon(self._get_icon("share_icon"))
        self.share_btn.clicked.connect(self._share_messages)
        main_toolbar.addWidget(self.share_btn)
        
        profile_toolbar = QToolBar("Profile")
        profile_toolbar.setObjectName("ProfileToolbar")
        if profile_toolbar.layout():
            profile_toolbar.layout().setSpacing(10)
        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(self._get_icon("user_icon"))
        self.profile_btn.clicked.connect(self._show_profile)
        profile_toolbar.addWidget(self.profile_btn)
        self.addToolBar(Qt.TopToolBarArea, profile_toolbar)

    def _create_chat_history_dock(self):
        self.history_dock = QDockWidget("Chat History", self)
        self.history_dock.setObjectName("ChatHistoryDock")
        self.history_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Ensure sufficient width for displaying content.
        self.history_dock.setMinimumWidth(300)
        
        self.history_list = QListWidget()
        self.history_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Remove explicit styling so global styles apply.
        self.history_list.setStyleSheet("")
        self.history_dock.setWidget(self.history_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.history_dock)
        self.history_dock.hide()

    def _create_main_interface(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        self.header_label = QLabel("AI Assistant Chat")
        self.header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Internal AI (Mistral)", "External AI (OpenAI)"])
        self.service_combo.setCurrentIndex(0)
        header_layout.addWidget(self.service_combo)
        layout.addWidget(header_widget)

        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll_area, 1)

        input_layout = QHBoxLayout()
        self.upload_btn = QPushButton()
        self.upload_btn.setIcon(self._get_icon("upload_icon"))
        self.upload_btn.setToolTip("Upload File")
        self.upload_btn.clicked.connect(self._upload_file)
        input_layout.addWidget(self.upload_btn, 0)
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.message_input, 1)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn, 0)
        layout.addLayout(input_layout)

        self.typing_indicator = QLabel("AI is preparing")
        self.typing_indicator.hide()
        layout.addWidget(self.typing_indicator)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready", 3000)

    # =========================================================================
    # Core Functionality
    # =========================================================================
    def _send_message(self):
        query = self.message_input.text().strip()
        print(self.user.user_id)
        if not query:
            self._show_input_error("Message cannot be empty")
            return

        timestamp = QDateTime.currentDateTime()
        self._append_message("You", query, timestamp)
        self._add_to_history("You", query, timestamp)
        self.message_input.clear()
        
        self.send_btn.setEnabled(False)
        self._show_typing_indicator()

        use_external = "External" in self.service_combo.currentText()
        self._current_worker = AIWorker(
            self.system, self.user, query, use_external
        )
        self._current_worker.response_received.connect(self._handle_response)
        self._current_worker.error_occurred.connect(self._handle_error)
        self._current_worker.start()

    def _handle_response(self, response):
        self._hide_typing_indicator()
        self.send_btn.setEnabled(True)
        sender = self.service_combo.currentText()
        timestamp = QDateTime.currentDateTime()
        self._append_message(sender, response.content, timestamp)
        self._add_to_history(sender, response.content, timestamp)

    def _handle_error(self, error: str):
        self._hide_typing_indicator()
        self.send_btn.setEnabled(True)
        timestamp = QDateTime.currentDateTime()
        self._append_message("System", f"Error: {error}", timestamp, is_error=True)
        self._add_to_history("System", f"Error: {error}", timestamp)

    # =========================================================================
    # Enhanced Features: Animated Typing Indicator
    # =========================================================================
    def _show_typing_indicator(self):
        self.ellipsis_count = 0
        self.typing_indicator.setText("AI is preparing")
        self.typing_indicator.show()
        self._typing_indicator_active = True
        self.typing_timer.start(500)

    def _update_typing_indicator(self):
        self.ellipsis_count = (self.ellipsis_count + 1) % 4
        dots = '.' * self.ellipsis_count
        self.typing_indicator.setText("AI is preparing" + dots)

    def _hide_typing_indicator(self):
        if self._typing_indicator_active:
            self.typing_timer.stop()
            self.typing_indicator.hide()
            self._typing_indicator_active = False

    def _append_message(self, sender: str, message: str, 
                        timestamp: QDateTime, is_error=False):
        msg_widget = ChatMessageWidget(sender, message, timestamp, is_error)
        self.chat_layout.addWidget(msg_widget)
        scroll_bar = self.chat_scroll_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def _add_to_history(self, sender: str, message: str, timestamp: QDateTime):
        # Debug: print the data being passed.
        print(f"DEBUG: _add_to_history: sender={sender}, message={message}, timestamp={timestamp.toString()}")
        item = QListWidgetItem()
        item.setData(Qt.UserRole, (sender, message, timestamp))
        
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Explicitly set text colors for visibility.
        if self._dark_theme:
            header_color = "#FFFFFF"
            content_color = "#FFFFFF"
        else:
            header_color = "#000000"
            content_color = "#000000"
        
        # Add explicit background-color: transparent in the style.
        header = QLabel(f"{sender} - {timestamp.toString('MMM d h:mm AP')}")
        header.setStyleSheet(f"background-color: transparent; color: {header_color}; font-size: 12px;")
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Ensure transparency attribute is set.
        header.setAttribute(Qt.WA_TranslucentBackground)
        
        content = QLabel(message)
        content.setStyleSheet(f"background-color: transparent; color: {content_color}; font-size: 13px;")
        content.setWordWrap(True)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content.setAttribute(Qt.WA_TranslucentBackground)
        
        layout.addWidget(header)
        layout.addWidget(content)
        
        item.setSizeHint(widget.sizeHint())
        self.history_list.addItem(item)
        self.history_list.setItemWidget(item, widget)
        self._message_history.append((sender, message, timestamp))

    def _load_history_item(self, index):
        item = self.history_list.item(index.row())
        data = item.data(Qt.UserRole)
        # Debug: print the data loaded from the history item.
        print(f"DEBUG: _load_history_item: data={data}")
        sender, message, timestamp = data
        self._append_message(sender, message, timestamp)

    # =========================================================================
    # Theme & Styling
    # =========================================================================
    def _apply_theme(self):
        palette = QPalette()
        if self._dark_theme:
            palette.setColor(QPalette.Window, QColor("#2C3E50"))
            palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
            palette.setColor(QPalette.Base, QColor("#34495E"))
            palette.setColor(QPalette.Text, QColor("#FFFFFF"))
            palette.setColor(QPalette.Button, QColor("#16A085"))
            palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
            palette.setColor(QPalette.Highlight, QColor("#1ABC9C"))
        else:
            palette.setColor(QPalette.Window, QColor("#F5F6FA"))
            palette.setColor(QPalette.WindowText, QColor("#000000"))
            palette.setColor(QPalette.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.Text, QColor("#000000"))
            palette.setColor(QPalette.Button, QColor("#3498DB"))
            palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
            palette.setColor(QPalette.Highlight, QColor("#2980B9"))

        self.setPalette(palette)
        self._update_stylesheets()

    def _update_stylesheets(self):
        base_style = """
            QMainWindow {
                background-color: $WINDOW;
            }
            QToolBar {
                background: $BASE;
                border-bottom: 1px solid $HIGHLIGHT;
                padding: 4px;
            }
            QComboBox, QLineEdit, QScrollArea, QLabel {
                background: $BASE;
                border: 1px solid $HIGHLIGHT;
                border-radius: 4px;
                padding: 6px;
                color: $TEXT;
            }
            QPushButton {
                background: $HIGHLIGHT;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: $BUTTON_TEXT;
            }
            QPushButton:disabled {
                background: $DISABLED;
            }
            QStatusBar {
                background: $BASE;
                color: $TEXT;
            }
            QDockWidget {
                background-color: $DOCK_BACKGROUND;
                color: $TEXT;
                border: 1px solid $HIGHLIGHT;
            }
            QDockWidget::title {
                background: $HIGHLIGHT;
                padding: 4px;
                text-align: center;
                color: $BUTTON_TEXT;
            }
            QListWidget {
                background-color: $DOCK_BACKGROUND;
                border: none;
                color: $TEXT;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid $HIGHLIGHT;
            }
            QListWidget::item:hover {
                background-color: $HIGHLIGHT;
            }
            QListWidget::item:selected {
                background-color: $HIGHLIGHT;
            }
        """

        if self._dark_theme:
            style = base_style.replace("$WINDOW", "#2C3E50") \
                             .replace("$BASE", "#34495E") \
                             .replace("$HIGHLIGHT", "#16A085") \
                             .replace("$TEXT", "#FFFFFF") \
                             .replace("$BUTTON_TEXT", "white") \
                             .replace("$DISABLED", "#7F8C8D") \
                             .replace("$DOCK_BACKGROUND", "#34495E")
        else:
            style = base_style.replace("$WINDOW", "#F5F6FA") \
                             .replace("$BASE", "white") \
                             .replace("$HIGHLIGHT", "#3498DB") \
                             .replace("$TEXT", "#000000") \
                             .replace("$BUTTON_TEXT", "white") \
                             .replace("$DISABLED", "#BDC3C7") \
                             .replace("$DOCK_BACKGROUND", "white")

        self.setStyleSheet(style)
        self.header_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {"#1ABC9C" if self._dark_theme else "#3498DB"};
            padding: 15px;
            border-bottom: 2px solid {"#16A085" if self._dark_theme else "#3498DB"};
        """)

    # =========================================================================
    # Settings & State Management
    # =========================================================================
    def _load_settings(self):
        settings = QSettings("YourCompany", "AIChat")
        self.restoreState(settings.value("windowState", b""))
        self.restoreGeometry(settings.value("windowGeometry", b""))
        self._dark_theme = settings.value("darkTheme", True, type=bool)

    def closeEvent(self, event):
        settings = QSettings("YourCompany", "AIChat")
        settings.setValue("windowState", self.saveState())
        settings.setValue("windowGeometry", self.saveGeometry())
        settings.setValue("darkTheme", self._dark_theme)
        super().closeEvent(event)

    # =========================================================================
    # Helper Methods
    # =========================================================================
    def _create_default_user(self):
        from ..models.employee import Employee
        return Employee(user_id=2, username="employee", 
                        hashed_password="", fullname="Employee")

    def _get_icon(self, name: str) -> QIcon:
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{name}.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon.fromTheme(name)

    def _show_input_error(self, message: str):
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                background-color: #FDEDEF;
            }
        """)
        self.status_bar.showMessage(message, 3000)
        QTimer.singleShot(2000, lambda: self.message_input.setStyleSheet(""))

    def toggle_chat_history(self):
        self.history_dock.setVisible(not self.history_dock.isVisible())

    def _toggle_theme(self):
        self._dark_theme = not self._dark_theme
        self._apply_theme()

    def _show_profile(self):
        profile = f"""
        <b>Username:</b> {self.user.username}<br>
        <b>Full Name:</b> {self.user.fullname}<br>
        <b>Role:</b> {type(self.user).__name__}
        """
        QMessageBox.information(self, "User Profile", profile)

    def _export_chat(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Chat", "", "Text Files (*.txt);;JSON Files (*.json)"
        )
        if not path:
            return

        try:
            if path.endswith(".json"):
                data = [{
                    "sender": sender,
                    "message": message,
                    "timestamp": timestamp.toString(Qt.ISODate)
                } for sender, message, timestamp in self._message_history]
                
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(path, 'w') as f:
                    for sender, message, timestamp in self._message_history:
                        f.write(f"[{timestamp.toString()}] {sender}: {message}\n")
                        
            self.status_bar.showMessage(f"Chat exported to {path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export chat: {str(e)}")

    def _show_search(self):
        text, ok = QInputDialog.getText(self, "Search Chat", "Search term:")
        if ok and text:
            self._search_messages(text)

    def _search_messages(self, term: str):
        # TODO: Implement search highlighting
        pass

    def _share_messages(self):
        chat_text = ""
        count = self.chat_layout.count()
        for i in range(count):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                sender = widget.sender_label.text()
                message = widget.content.text()
                chat_text += f"{sender}: {message}\n"
        QGuiApplication.clipboard().setText(chat_text)
        self.status_bar.showMessage("Chat copied to clipboard", 3000)

    def _upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload File", "", "All Files (*)")
        if file_path:
            timestamp = QDateTime.currentDateTime()
            upload_message = f"Uploaded file: {os.path.basename(file_path)}"
            self._append_message("You", upload_message, timestamp)
            self._add_to_history("You", upload_message, timestamp)

# =============================================================================
# Main Function
# =============================================================================
def main():
    system = System(external_api_key="initial_api_key_12345")
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    icon_path = os.path.join(os.path.dirname(__file__), "icons", "app_icon.png")
    app.setWindowIcon(QIcon(icon_path))
    
    dashboard = EmployeeChatDashboard(system=system)
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
