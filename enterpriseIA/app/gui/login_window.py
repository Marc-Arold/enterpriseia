import sys
from ..system import System as system
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class AuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.system = system
        self.setWindowTitle("Authentification des utilisateurs")
        self.setMinimumSize(500, 500)
        self.setWindowIcon(QIcon("icons/app_icon.png"))  # Ensure an icon exists at this path

        # Define the style for the window and its widgets
        self.setStyleSheet("""
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
            QSpacerItem {
                background-color: transparent;
            }
        """)

        self.initUI()

    def initUI(self):
        # Central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Title label
        title_label = QLabel("Votre IA en Toute Sécurité")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Spacer before tabs
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.create_login_tab()
        self.create_register_tab()

        # Spacer after tabs
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # -------------------- Login Tab --------------------
    def create_login_tab(self):
        login_tab = QWidget()
        self.tabs.addTab(login_tab, "Login")
        layout = QVBoxLayout()
        login_tab.setLayout(layout)

        # Form layout for login inputs
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setVerticalSpacing(20)
        layout.addLayout(form_layout)

        # Username input
        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        form_layout.addRow(QLabel("Username:"), self.login_username_input)

        # Password input
        self.login_password_input = QLineEdit()
        self.login_password_input.setEchoMode(QLineEdit.Password)
        self.login_password_input.setPlaceholderText("Entrez votre mot de passe")
        form_layout.addRow(QLabel("Password:"), self.login_password_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button, alignment=Qt.AlignCenter)

    def handle_login(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation", "Veuillez entrer le nom d'utilisateur et le mot de passe.")
            return

        # Authenticate via the system
        user = system.authenticateUser(self, username=username, password=password)
        if user:

            #user_info = self.system.get_user_info(username)
            user_info_name = user.getUsername()
            QMessageBox.information(
                self,
                "Connexion Réussie",
                f"Bienvenue, {user_info_name}!\n"
                f"Département: {""}"
            )
            self.login_username_input.clear()
            self.login_password_input.clear()
        else:
            QMessageBox.critical(self, "Échec de Connexion", "Nom d'utilisateur ou mot de passe invalide.")

    # -------------------- Register Tab --------------------
    def create_register_tab(self):
        register_tab = QWidget()
        self.tabs.addTab(register_tab, "Register")
        layout = QVBoxLayout()
        register_tab.setLayout(layout)

        # Form layout for registration inputs
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setVerticalSpacing(20)
        layout.addLayout(form_layout)

        # Full Name
        self.register_fullname_input = QLineEdit()
        self.register_fullname_input.setPlaceholderText("Entrez votre nom complet")
        form_layout.addRow(QLabel("Nom Complet:"), self.register_fullname_input)

        # Department
        self.register_department_input = QLineEdit()
        self.register_department_input.setPlaceholderText("Entrez votre département")
        form_layout.addRow(QLabel("Départment:"), self.register_department_input)

        # Username
        self.register_username_input = QLineEdit()
        self.register_username_input.setPlaceholderText("Choisissez un nom d'utilisateur")
        form_layout.addRow(QLabel("Username:"), self.register_username_input)

        # Password
        self.register_password_input = QLineEdit()
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_password_input.setPlaceholderText("Choisissez un mot de passe")
        form_layout.addRow(QLabel("Password:"), self.register_password_input)

        # Register button
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.handle_register)
        layout.addWidget(register_button, alignment=Qt.AlignCenter)

    def handle_register(self):
        fullname = self.register_fullname_input.text().strip()
        print(fullname)
        department = self.register_department_input.text().strip()
        print(department)
        username = self.register_username_input.text().strip()
        print(username)
        password = self.register_password_input.text().strip()
        print(password)

        if not fullname or not department or not username or not password:
            QMessageBox.warning(self, "Validation", "Tous les champs sont requis.")
            return

        # Attempt registration via the system
        print(username, password, fullname, department)
        success = system.createUser(self, username=username, password=password, fullname=fullname, department=department)
        print(success)
        if success:
            QMessageBox.information(self, "Inscription Réussie", "Utilisateur inscrit avec succès.")
            self.clear_register_form()
            self.tabs.setCurrentIndex(0)  # Switch to the Login tab
        else:
            QMessageBox.critical(self, "Échec de l'Inscription", "Le nom d'utilisateur existe déjà.")

    def clear_register_form(self):
        self.register_fullname_input.clear()
        self.register_department_input.clear()
        self.register_username_input.clear()
        self.register_password_input.clear()

def main():
    # Example system class with mock methods for demonstration
    # class MockSystem:
    #     def __init__(self):
    #         self.users = {}

    #     def authenticate_user(self, username, password):
    #         if username in self.users and self.users[username]["password"] == password:
    #             return True
    #         return False

    #     def get_user_info(self, username):
    #         return self.users.get(username, {})

    #     def register_user(self, username, password, fullname, department):
    #         if username in self.users:
    #             return False
    #         self.users[username] = {"password": password, "fullname": fullname, "department": department}
    #         return True

    # # Initialize the system
    # system = MockSystem()
    # system.register_user("admin", "admin123", "Administrateur", "Informatique")

    app = QApplication(sys.argv)
    auth_app = AuthApp()
    auth_app.show()
    sys.exit(app.exec())

# Uncomment the lines below if running this script directly:
if __name__ == "__main__":
    main()
