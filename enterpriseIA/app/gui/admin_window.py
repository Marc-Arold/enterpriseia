import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QScrollArea,
    QGroupBox, QFormLayout, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPixmap, QBrush, QColor

from ..system import System  # Adjust the import as needed


class AdminDashboard(QMainWindow):
    def __init__(self, system):
        super().__init__()
        self.system = system

        # Create or obtain an authenticated admin user.
        # Ensure this admin has the "CONFIGURE_SYSTEM" permission assigned in the DB.
        from ..models.admin import Admin
        self.admin_user = Admin(user_id=1, username="admin", hashed_password="", fullname="Administrator")

        self.setWindowTitle("Admin Dashboard")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.setStyleSheet("""
            QMainWindow { background-color: #2C3E50; }
            QLabel#GroupBoxTitle { font-size: 16px; font-weight: bold; color: #ECF0F1; }
            QLabel { font-size: 14px; color: #ECF0F1; }
            QPushButton { padding: 8px 16px; background-color: #1ABC9C; color: #2C3E50; border: none; border-radius: 5px; font-size: 14px; font-weight: bold; min-width: 100px; }
            QPushButton:hover { background-color: #16A085; color: #ECF0F1; }
            QLineEdit { padding: 8px; border: 2px solid #34495E; border-radius: 5px; background-color: #34495E; color: #ECF0F1; font-size: 14px; }
            QLineEdit:focus { border: 2px solid #1ABC9C; }
            QTableWidget { background-color: #34495E; color: #ECF0F1; border: 1px solid #1ABC9C; }
            QTableWidget::item:selected { background-color: #1ABC9C; color: #2C3E50; }
            QCheckBox { color: #ECF0F1; font-size: 14px; }
            QGroupBox { border: 2px solid #1ABC9C; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; color: #ECF0F1; font-size: 16px; font-weight: bold; }
            QTabWidget::pane { border: none; background-color: #2C3E50; }
            QTabBar::tab { background: #34495E; padding: 10px; font: 14pt "Helvetica"; color: #ECF0F1; margin: 2px; border-radius: 5px; }
            QTabBar::tab:selected { background: #1ABC9C; color: #2C3E50; }
            QScrollArea { background-color: #34495E; }
            QScrollBar:vertical { border: none; background: #34495E; width: 12px; margin: 0px; }
            QScrollBar::handle:vertical { background: #1ABC9C; min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        self.initUI()

    def load_icon(self, path, size=(24, 24)):
        if not os.path.exists(path):
            print(f"Icon not found: {path}")
            return QIcon()
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Failed to load pixmap: {path}")
            return QIcon()
        return QIcon(pixmap.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        title_label = QLabel("Admin Dashboard")
        title_label.setObjectName("GroupBoxTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        main_layout.addWidget(title_label)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs)
        self.tabs.currentChanged.connect(self.animate_tab_change)

        self.create_permission_tab()
        self.create_role_tab()
        self.create_model_tab()
        self.create_api_tab()

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

    def animate_tab_change(self, index):
        widget = self.tabs.widget(index)
        widget.setGraphicsEffect(None)
        opacity_effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity_effect)
        self.animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    # -------------------- Manage Permissions Tab --------------------
    def create_permission_tab(self):
        permission_tab = QWidget()
        self.tabs.addTab(permission_tab, "Manage Permissions")
        layout = QVBoxLayout()
        permission_tab.setLayout(layout)

        add_perm_group = QGroupBox("Add New Permission")
        add_perm_layout = QVBoxLayout()
        add_perm_group.setLayout(add_perm_layout)
        form_layout = QFormLayout()
        add_perm_layout.addLayout(form_layout)

        self.perm_name_input = QLineEdit()
        self.perm_name_input.setPlaceholderText("Enter permission name")
        form_layout.addRow(QLabel("Permission Name:"), self.perm_name_input)

        self.perm_desc_input = QLineEdit()
        self.perm_desc_input.setPlaceholderText("Enter description (optional)")
        form_layout.addRow(QLabel("Description:"), self.perm_desc_input)

        add_perm_button = QPushButton("Add Permission")
        add_perm_button.setIcon(self.load_icon("icons/add_permission_icon.png"))
        add_perm_button.clicked.connect(self.add_permission)
        add_perm_layout.addWidget(add_perm_button, alignment=Qt.AlignRight)

        layout.addWidget(add_perm_group)

        existing_perm_group = QGroupBox("Existing Permissions")
        existing_perm_layout = QVBoxLayout()
        existing_perm_group.setLayout(existing_perm_layout)

        self.perm_table = QTableWidget()
        self.perm_table.setColumnCount(2)
        self.perm_table.setHorizontalHeaderLabels(["Name", "Description"])
        self.perm_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.perm_table.setEditTriggers(QTableWidget.NoEditTriggers)
        existing_perm_layout.addWidget(self.perm_table)
        layout.addWidget(existing_perm_group)

        self.refresh_permissions()

    def add_permission(self):
        name = self.perm_name_input.text().strip()
        description = self.perm_desc_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Permission name is required.")
            return

        result = self.system.createPermission(self.admin_user, permission_name=name, description=description)
        if "created" in result.lower():
            QMessageBox.information(self, "Success", result)
            self.perm_name_input.clear()
            self.perm_desc_input.clear()
            self.refresh_permissions()
            self.refresh_roles_permissions()
        else:
            QMessageBox.critical(self, "Error", result)

    def refresh_permissions(self):
        try:
            from databaseHandler import get_all_permissions
            permissions = get_all_permissions()
            print("Retrieved permissions:", permissions)  # Debug print
        except Exception as e:
            permissions = []
            print(f"Error fetching permissions: {e}")

        self.perm_table.setRowCount(len(permissions))
        if not permissions:
            self.perm_table.setRowCount(1)
            item = QTableWidgetItem("No permissions found")
            item.setForeground(QBrush(QColor("red")))
            self.perm_table.setItem(0, 0, item)
            self.perm_table.setItem(0, 1, QTableWidgetItem(""))
            return

        for row, perm in enumerate(permissions):
            # Since perm is a tuple: (id, name, description)
            name_item = QTableWidgetItem(perm[1])
            desc_item = QTableWidgetItem(perm[2])
            name_item.setForeground(QBrush(QColor("#ECF0F1")))
            desc_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.perm_table.setItem(row, 0, name_item)
            self.perm_table.setItem(row, 1, desc_item)

    # -------------------- Manage Roles Tab --------------------
    def create_role_tab(self):
        role_tab = QWidget()
        self.tabs.addTab(role_tab, "Manage Roles")
        layout = QVBoxLayout()
        role_tab.setLayout(layout)

        add_role_group = QGroupBox("Add New Role")
        add_role_layout = QVBoxLayout()
        add_role_group.setLayout(add_role_layout)
        form_layout = QFormLayout()
        add_role_layout.addLayout(form_layout)

        self.role_name_input = QLineEdit()
        self.role_name_input.setPlaceholderText("Enter role name")
        form_layout.addRow(QLabel("Role Name:"), self.role_name_input)

        self.role_desc_input = QLineEdit()
        self.role_desc_input.setPlaceholderText("Enter description (optional)")
        form_layout.addRow(QLabel("Description:"), self.role_desc_input)

        perms_label_layout = QHBoxLayout()
        perms_icon = QLabel()
        perms_pixmap = QPixmap("icons/add_role_icon.png")
        if not perms_pixmap.isNull():
            perms_icon.setPixmap(perms_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        perms_label = QLabel("Assign Permissions:")
        perms_label.setFont(QFont("Helvetica", 14, QFont.Bold))
        perms_label_layout.addWidget(perms_icon)
        perms_label_layout.addWidget(perms_label)
        perms_label_layout.addStretch()
        add_role_layout.addLayout(perms_label_layout)

        self.perm_scroll = QScrollArea()
        self.perm_scroll.setWidgetResizable(True)
        self.perm_container = QWidget()
        self.perm_layout = QVBoxLayout()
        self.perm_container.setLayout(self.perm_layout)
        self.perm_scroll.setWidget(self.perm_container)
        add_role_layout.addWidget(self.perm_scroll)

        self.perm_checkboxes = {}
        try:
            from databaseHandler import get_all_permissions
            permissions = get_all_permissions()
            print("Permissions for roles:", permissions)  # Debug print
        except Exception as e:
            permissions = []
            print(f"Error fetching permissions for roles: {e}")
        for perm in permissions:
            # Treat perm as a tuple; get the name from index 1.
            perm_name = perm[1]
            checkbox = QCheckBox(perm_name)
            checkbox.setStyleSheet("QCheckBox { color: #2C3E50; font-size: 14px; }")
            self.perm_layout.addWidget(checkbox)
            self.perm_checkboxes[perm_name] = checkbox

        add_role_button = QPushButton("Add Role")
        add_role_button.setIcon(self.load_icon("icons/add_role_icon.png"))
        add_role_button.clicked.connect(self.add_role)
        add_role_layout.addWidget(add_role_button, alignment=Qt.AlignRight)
        layout.addWidget(add_role_group)

        existing_role_group = QGroupBox("Existing Roles")
        existing_role_layout = QVBoxLayout()
        existing_role_group.setLayout(existing_role_layout)

        self.role_table = QTableWidget()
        self.role_table.setColumnCount(3)
        self.role_table.setHorizontalHeaderLabels(["Name", "Description", "Permissions"])
        self.role_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.role_table.setEditTriggers(QTableWidget.NoEditTriggers)
        existing_role_layout.addWidget(self.role_table)
        layout.addWidget(existing_role_group)

        self.refresh_roles()

    def add_role(self):
        name = self.role_name_input.text().strip()
        description = self.role_desc_input.text().strip()
        selected_perms = [perm for perm, cb in self.perm_checkboxes.items() if cb.isChecked()]
        if not name:
            QMessageBox.warning(self, "Validation Error", "Role name is required.")
            return
        if not selected_perms:
            QMessageBox.warning(self, "Validation Error", "At least one permission must be selected.")
            return

        role_result = self.system.createRole(self.admin_user, role_name=name, description=description)
        if "created" in role_result.lower():
            try:
                from databaseHandler import get_role_by_name, get_permission_by_name
                role_data = get_role_by_name(name)
                if role_data:
                    # role_data is a tuple: (id, name, description, ...)
                    role_id = role_data[0]
                    attach_errors = []
                    for perm in selected_perms:
                        perm_data = get_permission_by_name(perm)
                        if perm_data:
                            # perm_data is a tuple: (id, name, description)
                            perm_id = perm_data[0]
                            attach_result = self.system.attachPermissionToRole(self.admin_user, role_id, perm_id)
                            if "denied" in attach_result.lower():
                                attach_errors.append(f"{perm}: {attach_result}")
                        else:
                            attach_errors.append(f"{perm}: not found")
                    if attach_errors:
                        QMessageBox.warning(self, "Partial Success", 
                                              "Role created but some permissions were not attached:\n" + "\n".join(attach_errors))
                    else:
                        QMessageBox.information(self, "Success", f"Role '{name}' created with permissions attached.")
                else:
                    QMessageBox.warning(self, "Warning", "Role was created but could not be retrieved to attach permissions.")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Role created but error attaching permissions: {str(e)}")
            self.role_name_input.clear()
            self.role_desc_input.clear()
            for cb in self.perm_checkboxes.values():
                cb.setChecked(False)
            self.refresh_roles()
        else:
            QMessageBox.critical(self, "Error", role_result)

    def refresh_roles(self):
        try:
            from databaseHandler import get_all_roles
            roles = get_all_roles()
            print("Retrieved roles:", roles)  # Debug print
        except Exception as e:
            roles = []
            print(f"Error fetching roles: {e}")
        self.role_table.setRowCount(len(roles))
        if not roles:
            self.role_table.setRowCount(1)
            item = QTableWidgetItem("No roles found")
            item.setForeground(QBrush(QColor("red")))
            self.role_table.setItem(0, 0, item)
            self.role_table.setItem(0, 1, QTableWidgetItem(""))
            self.role_table.setItem(0, 2, QTableWidgetItem(""))
            return

        for row, role in enumerate(roles):
            # Treat role as a tuple: (id, name, description, permissions)
            name_item = QTableWidgetItem(role[1])
            desc_item = QTableWidgetItem(role[2])
            # If role tuple has a fourth element containing permissions:
            if len(role) > 3 and role[3]:
                perms = ", ".join(role[3])
            else:
                perms = "None"
            perms_item = QTableWidgetItem(perms)
            name_item.setForeground(QBrush(QColor("#ECF0F1")))
            desc_item.setForeground(QBrush(QColor("#ECF0F1")))
            perms_item.setForeground(QBrush(QColor("#ECF0F1")))
            self.role_table.setItem(row, 0, name_item)
            self.role_table.setItem(row, 1, desc_item)
            self.role_table.setItem(row, 2, perms_item)

    def refresh_roles_permissions(self):
        # Refresh the permission checkboxes in the roles tab.
        for i in reversed(range(self.perm_layout.count())):
            widget = self.perm_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.perm_checkboxes.clear()
        try:
            from databaseHandler import get_all_permissions
            permissions = get_all_permissions()
            print("Refreshing role permissions:", permissions)  # Debug print
        except Exception as e:
            permissions = []
            print(f"Error refreshing role permissions: {e}")
        for perm in permissions:
            checkbox = QCheckBox(perm[1])
            checkbox.setStyleSheet("QCheckBox { color: #ECF0F1; font-size: 14px; }")
            self.perm_layout.addWidget(checkbox)
            self.perm_checkboxes[perm[1]] = checkbox

    # -------------------- Load Models Tab --------------------
    def create_model_tab(self):
        model_tab = QWidget()
        self.tabs.addTab(model_tab, "Load Models")
        layout = QVBoxLayout()
        model_tab.setLayout(layout)

        load_model_group = QGroupBox("Load Local AI Model")
        load_model_layout = QVBoxLayout()
        load_model_group.setLayout(load_model_layout)

        select_layout = QHBoxLayout()
        self.select_model_button = QPushButton("Select Model File")
        self.select_model_button.setIcon(self.load_icon("icons/load_model_icon.png"))
        self.select_model_button.clicked.connect(self.select_model_file)
        self.selected_model_label = QLabel("No file selected.")
        self.selected_model_label.setStyleSheet("color: #ECF0F1;")
        self.selected_model_label.setWordWrap(True)
        select_layout.addWidget(self.select_model_button)
        select_layout.addWidget(self.selected_model_label)
        load_model_layout.addLayout(select_layout)

        load_model_button = QPushButton("Load Model")
        load_model_button.setIcon(self.load_icon("icons/load_model_icon.png"))
        load_model_button.clicked.connect(self.load_model)
        load_model_layout.addWidget(load_model_button, alignment=Qt.AlignRight)
        layout.addWidget(load_model_group)

    def select_model_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select AI Model File",
            "",
            "AI Models (*.model *.pt *.pth);;All Files (*)"
        )
        if file_path:
            self.selected_model_label.setText(file_path)
            self.selected_model_label.setStyleSheet("color: #ECF0F1;")
        else:
            self.selected_model_label.setText("No file selected.")
            self.selected_model_label.setStyleSheet("color: gray;")

    def load_model(self):
        model_path = self.selected_model_label.text()
        if not model_path or model_path == "No file selected.":
            QMessageBox.warning(self, "Validation Error", "Please select a model file to load.")
            return
        result = self.system.adminLoadLocalModel(self.admin_user, model_path)
        if "loaded successfully" in result.lower():
            QMessageBox.information(self, "Success", result)
            self.selected_model_label.setText("No file selected.")
            self.selected_model_label.setStyleSheet("color: gray;")
        else:
            QMessageBox.critical(self, "Error", result)

    # -------------------- API Keys Tab --------------------
    def create_api_tab(self):
        api_tab = QWidget()
        self.tabs.addTab(api_tab, "API Keys")
        layout = QVBoxLayout()
        api_tab.setLayout(layout)

        change_api_group = QGroupBox("Change API Keys")
        change_api_layout = QVBoxLayout()
        change_api_group.setLayout(change_api_layout)

        api_key_layout = QHBoxLayout()
        api_key_icon = QLabel()
        api_key_pixmap = QPixmap("icons/api_key_icon.png")
        if not api_key_pixmap.isNull():
            api_key_icon.setPixmap(api_key_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        api_key_label = QLabel("New API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter new API key")
        api_key_layout.addWidget(api_key_icon)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        change_api_layout.addLayout(api_key_layout)

        update_api_button = QPushButton("Update API Key")
        update_api_button.setIcon(self.load_icon("icons/api_key_icon.png"))
        update_api_button.clicked.connect(self.update_api_key)
        change_api_layout.addWidget(update_api_button, alignment=Qt.AlignRight)

        self.current_api_label = QLabel(f"Current API Key: {self.system.externalAI.api_key}")
        change_api_layout.addWidget(self.current_api_label)
        layout.addWidget(change_api_group)

    def update_api_key(self):
        new_api_key = self.api_key_input.text().strip()
        if not new_api_key:
            QMessageBox.warning(self, "Validation Error", "API key cannot be empty.")
            return
        result = self.system.adminSetExternalAPIKey(self.admin_user, new_api_key)
        if "updated successfully" in result.lower():
            QMessageBox.information(self, "Success", result)
            self.api_key_input.clear()
            self.current_api_label.setText(f"Current API Key: {self.system.externalAI.api_key}")
        else:
            QMessageBox.critical(self, "Error", result)


def main():
    system = System(external_api_key="initial_api_key_12345")
    app = QApplication(sys.argv)
    admin_dashboard = AdminDashboard(system=system)
    admin_dashboard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
