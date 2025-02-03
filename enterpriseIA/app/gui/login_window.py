# login_window.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from ..system import System

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

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Instantiate the system backend once
        self.system = System()
        self.setWindowTitle("User Authentication")
        self.setMinimumSize(500, 500)
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.setStyleSheet(self.loadStyles())
        self.initUI()

    def loadStyles(self):
        return """
            /* General Styles */
            QMainWindow {
                background-color: #2C3E50;
            }
            QLabel#TitleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ECF0F1;
            }
            QLabel {
                font-size: 14px;
                color: #ECF0F1;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #34495E;
                border-radius: 5px;
                background-color: #34495E;
                color: #ECF0F1;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1ABC9C;
            }
            QPushButton {
                padding: 10px 20px;
                background-color: #1ABC9C;
                color: #2C3E50;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16A085;
                color: #ECF0F1;
            }
            QTabWidget::pane {
                border: none;
                background-color: #2C3E50;
            }
            QTabBar::tab {
                background: #34495E;
                padding: 10px;
                font: 14pt "Helvetica";
                color: #ECF0F1;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #1ABC9C;
                color: #2C3E50;
            }
        """

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("Votre IA en Toute Sécurité")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs)

        self.create_login_tab()
        self.create_register_tab()

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def create_login_tab(self):
        login_tab = QWidget()
        self.tabs.addTab(login_tab, "Login")
        layout = QVBoxLayout(login_tab)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setVerticalSpacing(20)
        layout.addLayout(form_layout)

        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        form_layout.addRow(QLabel("Username:"), self.login_username_input)

        self.login_password_input = QLineEdit()
        self.login_password_input.setEchoMode(QLineEdit.Password)
        self.login_password_input.setPlaceholderText("Entrez votre mot de passe")
        form_layout.addRow(QLabel("Password:"), self.login_password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button, alignment=Qt.AlignCenter)

    def create_register_tab(self):
        register_tab = QWidget()
        self.tabs.addTab(register_tab, "Register")
        layout = QVBoxLayout(register_tab)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setVerticalSpacing(20)
        layout.addLayout(form_layout)

        self.register_fullname_input = QLineEdit()
        self.register_fullname_input.setPlaceholderText("Entrez votre nom complet")
        form_layout.addRow(QLabel("Nom Complet:"), self.register_fullname_input)

        self.register_department_input = QLineEdit()
        self.register_department_input.setPlaceholderText("Entrez votre département")
        form_layout.addRow(QLabel("Départment:"), self.register_department_input)

        self.register_username_input = QLineEdit()
        self.register_username_input.setPlaceholderText("Choisissez un nom d'utilisateur")
        form_layout.addRow(QLabel("Username:"), self.register_username_input)

        self.register_password_input = QLineEdit()
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_password_input.setPlaceholderText("Choisissez un mot de passe")
        form_layout.addRow(QLabel("Password:"), self.register_password_input)

        self.register_password_confirm_input = QLineEdit()
        self.register_password_confirm_input.setEchoMode(QLineEdit.Password)
        self.register_password_confirm_input.setPlaceholderText("Confirmez votre mot de passe")
        form_layout.addRow(QLabel("Confirm Password:"), self.register_password_confirm_input)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.handle_register)
        layout.addWidget(register_button, alignment=Qt.AlignCenter)

    def handle_login(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation", "Veuillez entrer le nom d'utilisateur et le mot de passe.")
            return

        # Run authentication asynchronously to avoid UI blocking
        self.login_thread = QThread()
        self.login_worker = Worker(self.system.authenticateUser, username, password)
        self.login_worker.moveToThread(self.login_thread)
        self.login_thread.started.connect(self.login_worker.run)
        self.login_worker.finished.connect(self.process_login_result)
        self.login_worker.error.connect(self.process_login_error)
        self.login_worker.finished.connect(self.login_thread.quit)
        self.login_worker.finished.connect(self.login_worker.deleteLater)
        self.login_thread.finished.connect(self.login_thread.deleteLater)
        self.login_thread.start()

    def process_login_result(self, user):
        if user:
            QMessageBox.information(self, "Connexion Réussie", f"Bienvenue, {user.getUsername()}!")
            self.login_username_input.clear()
            self.login_password_input.clear()
            # Redirect the user based on the type of user object (Admin, DPO, or Employee)
            self.redirect_user(user)
        else:
            QMessageBox.critical(self, "Échec de Connexion", "Nom d'utilisateur ou mot de passe invalide.")

    def process_login_error(self, error_msg):
        QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {error_msg}")

    def handle_register(self):
        fullname = self.register_fullname_input.text().strip()
        department = self.register_department_input.text().strip()
        username = self.register_username_input.text().strip()
        password = self.register_password_input.text().strip()
        password_confirm = self.register_password_confirm_input.text().strip()

        if not fullname or not department or not username or not password or not password_confirm:
            QMessageBox.warning(self, "Validation", "Tous les champs sont requis.")
            return

        if password != password_confirm:
            QMessageBox.warning(self, "Validation", "Les mots de passe ne correspondent pas.")
            return

        # Run registration asynchronously
        self.register_thread = QThread()
        self.register_worker = Worker(self.system.createUser, username, password, fullname, department)
        self.register_worker.moveToThread(self.register_thread)
        self.register_thread.started.connect(self.register_worker.run)
        self.register_worker.finished.connect(self.process_register_result)
        self.register_worker.error.connect(self.process_register_error)
        self.register_worker.finished.connect(self.register_thread.quit)
        self.register_worker.finished.connect(self.register_worker.deleteLater)
        self.register_thread.finished.connect(self.register_thread.deleteLater)
        self.register_thread.start()

    def process_register_result(self, user_id):
        if user_id:
            QMessageBox.information(self, "Inscription Réussie", "Utilisateur inscrit avec succès.")
            self.clear_register_form()
            self.tabs.setCurrentIndex(0)  # Switch to login tab
        else:
            QMessageBox.critical(self, "Échec de l'Inscription", "Le nom d'utilisateur existe déjà.")

    def process_register_error(self, error_msg):
        QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {error_msg}")

    def clear_register_form(self):
        self.register_fullname_input.clear()
        self.register_department_input.clear()
        self.register_username_input.clear()
        self.register_password_input.clear()
        self.register_password_confirm_input.clear()

    def redirect_user(self, user):
        """
        Redirects the authenticated user to the appropriate interface based on the user type.
        """
        role = type(user).__name__
        if role == "Admin":
            from admin_window import AdminDashboard
            self.dashboard = AdminDashboard(system=self.system, admin_user=user)
        elif role == "DPO":
            from dpo_window import DPODashboard
            self.dashboard = DPODashboard(system=self.system, current_user=user)
        else:
            from .employee_window import EmployeeChatDashboard
            self.dashboard = EmployeeChatDashboard(system=self.system)
        self.dashboard.show()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
