import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QScrollArea, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QObject, QThread, Slot, Signal
from PySide6.QtGui import QIcon, QFont, QBrush, QColor

# Adjust as needed to match your package structure
from ..system import System  
from databaseHandler import get_users_by_username, get_user_by_id

class Worker(QObject):
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AdminDashboard(QMainWindow):
    def __init__(self, system, admin_user):
        super().__init__()
        self.system = system
        self.admin_user = admin_user

        self.setWindowTitle("Admin Dashboard")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        # Use the helper method to load the app icon with an absolute path.
        self.setWindowIcon(self._get_icon("app_icon"))

        # Main style settings
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2C3E50, stop:1 #243342
                );
            }
            QLabel#GroupBoxTitle {
                font-size: 18px;
                font-weight: bold;
                color: #ECF0F1;
                margin-left: 6px;
            }
            QLabel {
                font-size: 14px;
                color: #ECF0F1;
            }
            QPushButton {
                padding: 10px 16px;
                background-color: #1ABC9C;
                color: #2C3E50;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #16A085;
                color: #ECF0F1;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #34495E;
                border-radius: 5px;
                background-color: #34495E;
                color: #ECF0F1;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1ABC9C;
            }
            QTableWidget {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                gridline-color: #1ABC9C;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #1ABC9C;
                color: #2C3E50;
            }
            QTableWidget::horizontalHeader {
                background-color: #16A085;
                color: #ECF0F1;
                font-weight: bold;
            }
            QTableWidget::verticalHeader {
                background-color: #16A085;
                color: #ECF0F1;
                font-weight: bold;
            }
            QScrollArea {
                background-color: #34495E;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background: #34495E;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #1ABC9C;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QTabWidget::pane {
                border: 2px solid #16A085;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #34495E;
                padding: 10px;
                font: 14pt "Helvetica";
                color: #ECF0F1;
                margin: 4px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #1ABC9C;
                color: #2C3E50;
                font-weight: bold;
            }
        """)
        self.initUI()

    def _get_icon(self, name: str) -> QIcon:
        """
        Compute the absolute path for the icon relative to this file
        and return a QIcon object.
        """
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{name}.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon.fromTheme(name)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top navigation with title and "Go to Chat Interface" button
        nav_layout = QHBoxLayout()
        title_label = QLabel("Admin Dashboard")
        title_label.setObjectName("GroupBoxTitle")
        title_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        nav_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        nav_layout.addStretch()  # Push the button to the right

        chat_button = QPushButton("Go to Chat Interface")
        chat_button.clicked.connect(self.open_chat_interface)
        nav_layout.addWidget(chat_button)
        main_layout.addLayout(nav_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs)
        self.tabs.currentChanged.connect(self.animate_tab_change)

        # Create and add tabs
        self.create_permission_tab()
        self.create_role_tab()
        self.create_model_tab()
        self.create_api_tab()
        self.create_user_permissions_tab()

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

    def animate_tab_change(self, index):
        widget = self.tabs.widget(index)
        widget.setGraphicsEffect(None)
        opacity_effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity_effect)
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(500)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    # ---------------------------------------------------
    # Permissions Overview Tab (Read-Only)
    def create_permission_tab(self):
        permission_tab = QWidget()
        self.tabs.addTab(permission_tab, "Permissions Overview")
        layout = QVBoxLayout(permission_tab)

        info_label = QLabel("The following predefined permissions are available:")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        self.perm_table = QTableWidget()
        self.perm_table.setColumnCount(2)
        self.perm_table.setHorizontalHeaderLabels(["Name", "Description"])
        self.perm_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.perm_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.perm_table)

        self.refresh_permissions()

    def refresh_permissions(self):
        try:
            from databaseHandler import get_all_permissions
            permissions = get_all_permissions()
        except Exception:
            permissions = []

        if not permissions:
            self.perm_table.setRowCount(1)
            item = QTableWidgetItem("No permissions found")
            item.setForeground(QBrush(QColor("#ECF0F1")))
            self.perm_table.setItem(0, 0, item)
            self.perm_table.setItem(0, 1, QTableWidgetItem(""))
            return

        self.perm_table.setRowCount(len(permissions))
        for row_idx, perm in enumerate(permissions):
            name_item = QTableWidgetItem(perm[1])
            name_item.setForeground(QBrush(QColor("#ECF0F1")))
            desc_item = QTableWidgetItem(perm[2])
            desc_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.perm_table.setItem(row_idx, 0, name_item)
            self.perm_table.setItem(row_idx, 1, desc_item)

    # ---------------------------------------------------
    # Role Tab
    def create_role_tab(self):
        role_tab = QWidget()
        self.tabs.addTab(role_tab, "Manage Roles")
        layout = QVBoxLayout(role_tab)

        # Create new role layout
        create_role_layout = QHBoxLayout()
        self.new_role_name = QLineEdit()
        self.new_role_name.setPlaceholderText("Enter new role name")
        self.new_role_desc = QLineEdit()
        self.new_role_desc.setPlaceholderText("Enter role description")
        create_role_button = QPushButton("Create Role")
        create_role_button.clicked.connect(self.create_new_role)
        create_role_layout.addWidget(self.new_role_name)
        create_role_layout.addWidget(self.new_role_desc)
        create_role_layout.addWidget(create_role_button)
        layout.addLayout(create_role_layout)

        # Table to list existing roles
        self.role_table = QTableWidget()
        self.role_table.setColumnCount(2)
        self.role_table.setHorizontalHeaderLabels(["Role ID", "Role Name"])
        self.role_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.role_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.role_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.role_table.cellClicked.connect(self.load_role_permissions)
        layout.addWidget(self.role_table)

        refresh_roles_button = QPushButton("Refresh Roles")
        refresh_roles_button.clicked.connect(self.refresh_roles_table)
        layout.addWidget(refresh_roles_button, alignment=Qt.AlignLeft)

        # Permissions assignment area
        self.selected_role_id = None
        self.selected_role_label = QLabel("No role selected")
        layout.addWidget(self.selected_role_label)

        self.role_permissions_scroll = QScrollArea()
        self.role_permissions_scroll.setWidgetResizable(True)
        self.role_permissions_container = QWidget()
        self.role_permissions_container.setStyleSheet("background-color: #34495E; padding: 10px;")
        self.role_permissions_layout = QVBoxLayout(self.role_permissions_container)
        self.role_permissions_scroll.setWidget(self.role_permissions_container)
        layout.addWidget(self.role_permissions_scroll)

        save_role_perms_button = QPushButton("Save Role Permissions")
        save_role_perms_button.clicked.connect(self.save_role_permissions)
        layout.addWidget(save_role_perms_button, alignment=Qt.AlignRight)

        self.refresh_roles_table()

    def create_new_role(self):
        role_name = self.new_role_name.text().strip()
        role_desc = self.new_role_desc.text().strip()
        if not role_name:
            QMessageBox.warning(self, "Warning", "Role name cannot be empty.")
            return
        msg = self.system.createRole(self.admin_user, role_name, role_desc)
        QMessageBox.information(self, "Create Role", msg)
        self.refresh_roles_table()

    def refresh_roles_table(self):
        self.role_table.setRowCount(0)
        try:
            from databaseHandler import get_all_roles
            all_roles = get_all_roles()  
        except:
            all_roles = []
        self.role_table.setRowCount(len(all_roles))
        for row_idx, role_info in enumerate(all_roles):
            role_id_item = QTableWidgetItem(str(role_info[0]))
            role_id_item.setForeground(QBrush(QColor("#ECF0F1")))
            role_name_item = QTableWidgetItem(role_info[1])
            role_name_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.role_table.setItem(row_idx, 0, role_id_item)
            self.role_table.setItem(row_idx, 1, role_name_item)

    def load_role_permissions(self, row, column):
        role_id_item = self.role_table.item(row, 0)
        if role_id_item:
            self.selected_role_id = int(role_id_item.text())
            role_name_item = self.role_table.item(row, 1)
            role_name = role_name_item.text() if role_name_item else ""
            self.selected_role_label.setText(f"Selected Role: {role_name} (ID: {self.selected_role_id})")
            for i in reversed(range(self.role_permissions_layout.count())):
                widget = self.role_permissions_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            try:
                from databaseHandler import get_all_permissions
                permissions = get_all_permissions()
            except:
                permissions = []
            try:
                from databaseHandler import get_permissions_for_role
                role_perms = get_permissions_for_role(self.selected_role_id)
            except:
                role_perms = []
            role_perm_ids = set([rp[0] for rp in role_perms])
            self.role_perm_checkboxes = {}
            for perm in permissions:
                checkbox = QCheckBox(f"{perm[1]}: {perm[2]}")
                checkbox.setStyleSheet("""
                    QCheckBox { 
                        color: #FFFFFF;
                        background-color: transparent; 
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                        border: 2px solid #16A085;
                        background-color: transparent;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #1ABC9C;
                    }
                """)
                checkbox.setChecked(perm[0] in role_perm_ids)
                self.role_permissions_layout.addWidget(checkbox)
                self.role_perm_checkboxes[perm[0]] = checkbox

    def save_role_permissions(self):
        if self.selected_role_id is None:
            QMessageBox.warning(self, "Warning", "No role selected.")
            return
        try:
            from databaseHandler import get_permissions_for_role
            current_role_perms = get_permissions_for_role(self.selected_role_id)
        except:
            current_role_perms = []
        current_perm_ids = set([rp[0] for rp in current_role_perms])
        for perm_id, checkbox in self.role_perm_checkboxes.items():
            if checkbox.isChecked() and perm_id not in current_perm_ids:
                res = self.system.attachPermissionToRole(self.admin_user, self.selected_role_id, perm_id)
                print(res)
            elif not checkbox.isChecked() and perm_id in current_perm_ids:
                res = self.system.detachPermissionFromRole(self.admin_user, self.selected_role_id, perm_id)
                print(res)
        QMessageBox.information(self, "Success", "Role permissions updated.")
        row = self.role_table.currentRow()
        if row >= 0:
            self.load_role_permissions(row, 0)

    # ---------------------------------------------------
    # Model Tab (Load, List, Delete)
    def create_model_tab(self):
        model_tab = QWidget()
        self.tabs.addTab(model_tab, "Load Models")
        main_layout = QVBoxLayout(model_tab)
        instruction_label = QLabel("Enter a model name to load from Ollama:")
        main_layout.addWidget(instruction_label)
        model_input_layout = QHBoxLayout()
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("e.g., llama2, wizardLM...")
        model_load_button = QPushButton("Load Model")
        model_load_button.clicked.connect(self.load_model_from_ollama)
        model_input_layout.addWidget(self.model_name_edit)
        model_input_layout.addWidget(model_load_button)
        main_layout.addLayout(model_input_layout)
        self.model_load_status = QLabel("")
        main_layout.addWidget(self.model_load_status)
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(3)
        self.model_table.setHorizontalHeaderLabels(["Model ID", "Model Name", "Created At"])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.model_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.model_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.model_table)
        model_buttons_layout = QHBoxLayout()
        refresh_models_button = QPushButton("Refresh Models")
        refresh_models_button.clicked.connect(self.refresh_model_table)
        delete_model_button = QPushButton("Delete Selected Model")
        delete_model_button.clicked.connect(self.delete_selected_model)
        model_buttons_layout.addWidget(refresh_models_button)
        model_buttons_layout.addWidget(delete_model_button)
        main_layout.addLayout(model_buttons_layout)
        self.refresh_model_table()

    def load_model_from_ollama(self):
        model_name = self.model_name_edit.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Warning", "Model name cannot be empty.")
            return
        result = self.system.adminLoadLocalModel(self.admin_user, model_name)
        self.model_load_status.setText(result)
        self.refresh_model_table()

    def refresh_model_table(self):
        models = self.system.getAllModels()
        self.model_table.setRowCount(len(models))
        for row_idx, mod in enumerate(models):
            id_item = QTableWidgetItem(str(mod[0]))
            id_item.setForeground(QBrush(QColor("#ECF0F1")))
            name_item = QTableWidgetItem(mod[1])
            name_item.setForeground(QBrush(QColor("#ECF0F1")))
            date_item = QTableWidgetItem(str(mod[2]))
            date_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.model_table.setItem(row_idx, 0, id_item)
            self.model_table.setItem(row_idx, 1, name_item)
            self.model_table.setItem(row_idx, 2, date_item)

    def delete_selected_model(self):
        row = self.model_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "No model selected.")
            return
        model_id_item = self.model_table.item(row, 0)
        model_name_item = self.model_table.item(row, 1)
        if not model_id_item or not model_name_item:
            return
        model_id = int(model_id_item.text())
        model_name = model_name_item.text()
        msg = self.system.adminDeleteLocalModel(self.admin_user, model_id, model_name)
        QMessageBox.information(self, "Delete Model", msg)
        self.refresh_model_table()

    # ---------------------------------------------------
    # API Key Tab
    def create_api_tab(self):
        api_tab = QWidget()
        self.tabs.addTab(api_tab, "API Keys")
        layout = QVBoxLayout(api_tab)
        api_key_label = QLabel("Set or Update External Model API Key:")
        layout.addWidget(api_key_label)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter new API key here")
        layout.addWidget(self.api_key_edit)
        save_api_button = QPushButton("Save API Key")
        save_api_button.clicked.connect(self.save_external_api_key)
        layout.addWidget(save_api_button)
        self.api_status_label = QLabel("")
        layout.addWidget(self.api_status_label)

    def save_external_api_key(self):
        new_key = self.api_key_edit.text().strip()
        if not new_key:
            QMessageBox.warning(self, "Warning", "API key cannot be empty.")
            return
        result = self.system.adminSetExternalAPIKey(self.admin_user, new_key)
        self.api_status_label.setText(result)

    # ---------------------------------------------------
    # User Permissions Tab
    def create_user_permissions_tab(self):
        user_perm_tab = QWidget()
        self.tabs.addTab(user_perm_tab, "User Permissions")
        layout = QVBoxLayout(user_perm_tab)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter username or ID to search")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_users)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["User ID", "Username", "Full Name", "Department"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.cellClicked.connect(self.user_selected)
        layout.addWidget(self.users_table)
        self.selected_user_label = QLabel("No user selected")
        layout.addWidget(self.selected_user_label)
        self.permissions_scroll = QScrollArea()
        self.permissions_scroll.setWidgetResizable(True)
        self.permissions_container = QWidget()
        self.permissions_container.setStyleSheet("background-color: #34495E; padding: 10px;")
        self.permissions_layout = QVBoxLayout(self.permissions_container)
        self.permissions_scroll.setWidget(self.permissions_container)
        layout.addWidget(self.permissions_scroll)
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_user_permissions)
        layout.addWidget(save_button, alignment=Qt.AlignRight)
        self.user_perm_checkboxes = {}
        self.selected_user_id = None

    def search_users(self):
        query_str = self.search_input.text().strip()
        print(query_str)
        if query_str.isdigit():
            user_record = get_user_by_id(int(query_str))
            if user_record:
                users = [user_record]
            else:
                users = []
        else:
            users = get_users_by_username(query_str)
        self.users_table.setRowCount(len(users))
        for row_idx, user_rec in enumerate(users):
            id_item = QTableWidgetItem(str(user_rec[0]))
            id_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.users_table.setItem(row_idx, 0, id_item)
            name_item = QTableWidgetItem(user_rec[1])
            name_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.users_table.setItem(row_idx, 1, name_item)
            full_item = QTableWidgetItem(user_rec[3] if user_rec[3] else "")
            full_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.users_table.setItem(row_idx, 2, full_item)
            dept_item = QTableWidgetItem(user_rec[4] if user_rec[4] else "")
            dept_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.users_table.setItem(row_idx, 3, dept_item)

    def user_selected(self, row, column):
        user_id_item = self.users_table.item(row, 0)
        if user_id_item:
            self.selected_user_id = int(user_id_item.text())
            username = self.users_table.item(row, 1).text()
            self.selected_user_label.setText(f"Selected User: {username} (ID: {self.selected_user_id})")
            self.load_user_permissions(self.selected_user_id)
            
    def load_user_permissions(self, user_id):
        for i in reversed(range(self.permissions_layout.count())):
            widget = self.permissions_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.user_perm_checkboxes.clear()
        try:
            from databaseHandler import get_all_permissions
            all_perms = get_all_permissions()
        except:
            all_perms = []
        user_perms = self.system.getUserPermissions(user_id)
        user_perm_ids = set([perm[0] for perm in user_perms])
        for perm in all_perms:
            checkbox = QCheckBox(f"{perm[1]}: {perm[2]}")
            checkbox.setStyleSheet("""
                QCheckBox { 
                    color: #FFFFFF;
                    background-color: transparent; 
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #16A085;
                    background-color: transparent;
                }
                QCheckBox::indicator:checked {
                    background-color: #1ABC9C;
                }
            """)
            checkbox.setChecked(perm[0] in user_perm_ids)
            self.permissions_layout.addWidget(checkbox)
            self.user_perm_checkboxes[perm[0]] = checkbox
            
    def save_user_permissions(self):
        if self.selected_user_id is None:
            QMessageBox.warning(self, "Warning", "No user selected.")
            return
        current_user_perms = self.system.getUserPermissions(self.selected_user_id)
        current_perm_ids = set([perm[0] for perm in current_user_perms])
        for perm_id, checkbox in self.user_perm_checkboxes.items():
            if checkbox.isChecked() and perm_id not in current_perm_ids:
                res = self.system.addPermissionToUser(self.admin_user, self.selected_user_id, perm_id)
                print(res)
            elif not checkbox.isChecked() and perm_id in current_perm_ids:
                res = self.system.removePermissionFromUser(self.admin_user, self.selected_user_id, perm_id)
                print(res)
        QMessageBox.information(self, "Success", "User permissions updated.")
        self.load_user_permissions(self.selected_user_id)

    # ---------------------------------------------------
    # Navigation to Chat Interface
    def open_chat_interface(self):
        # Redirect: Close the current dashboard and open the chat interface in its place admin_user
        from .employee_window import EmployeeChatDashboard
        self.chat_interface = EmployeeChatDashboard(system=self.system, user=self.admin_user)
        self.chat_interface.show()
        self.close()

def main():
    from ..models.admin import Admin
    system_instance = System(external_api_key="initial_api_key_12345")
    admin_user = Admin(user_id=1, username="admin", hashed_password="", fullname="Administrator")
    app = QApplication(sys.argv)
    dashboard = AdminDashboard(system=system_instance, admin_user=admin_user)
    dashboard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()