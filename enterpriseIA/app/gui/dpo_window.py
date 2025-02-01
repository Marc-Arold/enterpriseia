import sys
import csv
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QGroupBox, QFormLayout,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon, QFont, QPalette, QColor

# --------------------- Mock Backend Implementations ---------------------

class MockSystem:
    """
    A mock backend system to simulate database interactions and business logic.
    This is solely for testing the DPO Dashboard independently.
    """
    def __init__(self):
        # In-memory storage for audit logs
        self.audit_logs = []
        self.populate_mock_logs()
    
    def populate_mock_logs(self):
        """
        Pre-populate some mock audit logs for testing purposes.
        """
        actions = ["CREATE_USER", "DELETE_USER", "MODIFY_USER", "LOGIN", "LOGOUT", "CHANGE_API_KEY"]
        users = ["admin", "johndoe", "janedoe", "alice", "bob"]
        for i in range(1, 51):  # Create 50 mock logs
            log = {
                'id': i,
                'timestamp': (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
                'user': users[i % len(users)],
                'action': actions[i % len(actions)],
                'details': f"Performed {actions[i % len(actions)]} action on user {users[(i+1) % len(users)]}."
            }
            self.audit_logs.append(log)
    
    def get_all_audit_logs(self):
        return self.audit_logs
    
    def filter_audit_logs(self, start_date=None, end_date=None, action=None, user=None, keyword=None):
        filtered_logs = self.audit_logs
        
        if start_date:
            filtered_logs = [log for log in filtered_logs if datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S") >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs if datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S") <= end_date]
        
        if action and action != "All":
            filtered_logs = [log for log in filtered_logs if log['action'] == action]
        
        if user and user != "All":
            filtered_logs = [log for log in filtered_logs if log['user'] == user]
        
        if keyword:
            filtered_logs = [log for log in filtered_logs if keyword.lower() in log['details'].lower()]
        
        return filtered_logs
    
    def export_audit_logs_to_csv(self, logs, file_path):
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['ID', 'Timestamp', 'User', 'Action', 'Details']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    writer.writerow({
                        'ID': log['id'],
                        'Timestamp': log['timestamp'],
                        'User': log['user'],
                        'Action': log['action'],
                        'Details': log['details']
                    })
            return True, "Logs exported successfully."
        except Exception as e:
            return False, str(e)

# --------------------------- DPODashboard Class ---------------------------

from datetime import datetime, timedelta

class DPODashboard(QMainWindow):
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.setWindowTitle("DPO Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Apply dark theme using stylesheets
        self.apply_dark_theme()
        
        # Set Window Icon (Optional)
        # self.setWindowIcon(QIcon("icons/app_icon.png"))  # Ensure you have an icon at this path
    
        # Initialize UI
        self.init_ui()
    
    def apply_dark_theme(self):
        """
        Apply a dark theme to the application using Qt stylesheets.
        """
        dark_palette = QPalette()

        # Base Colors
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
        
        # Highlight Colors
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Apply Stylesheet for additional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #2C3E50;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #16A085;
                color: #ECF0F1;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #1ABC9C;
            }
            QTreeWidget {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                font-size: 14px;
            }
            QTreeWidget::item:selected {
                background-color: #1ABC9C;
                color: #2C3E50;
            }
            QHeaderView::section {
                background-color: #1ABC9C;
                color: #2C3E50;
                padding: 4px;
                border: 1px solid #1ABC9C;
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox {
                border: 2px solid #1ABC9C;
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
        """)
    
    def init_ui(self):
        """
        Initialize the main UI components.
        """
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title Label
        title_label = QLabel("DPO Dashboard")
        title_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs)
        
        # Create Tabs
        self.create_view_logs_tab()
        self.create_audit_actions_tab()
    
    # -------------------- View Audit Logs Tab --------------------
    def create_view_logs_tab(self):
        """
        Create the 'View Audit Logs' tab.
        """
        view_logs_tab = QWidget()
        self.tabs.addTab(view_logs_tab, "View Audit Logs")
        
        # Layout for the tab
        layout = QVBoxLayout()
        view_logs_tab.setLayout(layout)
        
        # Filters GroupBox
        filters_group = QGroupBox("Filters")
        filters_layout = QFormLayout()
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Start Date
        self.start_date_edit = QLineEdit()
        self.start_date_edit.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addRow(QLabel("Start Date:"), self.start_date_edit)
        
        # End Date
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addRow(QLabel("End Date:"), self.end_date_edit)
        
        # Action Type
        self.action_combo = QLineEdit()
        self.action_combo.setPlaceholderText("Enter Action Type or 'All'")
        filters_layout.addRow(QLabel("Action Type:"), self.action_combo)
        
        # User
        self.user_combo = QLineEdit()
        self.user_combo.setPlaceholderText("Enter User or 'All'")
        filters_layout.addRow(QLabel("User:"), self.user_combo)
        
        # Keyword
        self.keyword_entry = QLineEdit()
        self.keyword_entry.setPlaceholderText("Enter Keyword")
        filters_layout.addRow(QLabel("Keyword:"), self.keyword_entry)
        
        # Buttons Layout
        buttons_layout = QHBoxLayout()
        apply_filter_btn = QPushButton("Apply Filters")
        apply_filter_btn.clicked.connect(self.apply_filters)
        reset_filter_btn = QPushButton("Reset Filters")
        reset_filter_btn.clicked.connect(self.reset_filters)
        buttons_layout.addWidget(apply_filter_btn)
        buttons_layout.addWidget(reset_filter_btn)
        layout.addLayout(buttons_layout)
        
        # Audit Logs TreeWidget
        self.logs_tree = QTreeWidget()
        self.logs_tree.setColumnCount(5)
        self.logs_tree.setHeaderLabels(["ID", "Timestamp", "User", "Action", "Details"])
        self.logs_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.logs_tree)
        
        # Export Button
        export_btn = QPushButton("Export Logs to CSV")
        export_btn.clicked.connect(self.export_logs)
        layout.addWidget(export_btn, alignment=Qt.AlignRight)
        
        # Populate the TreeWidget with all logs initially
        self.display_logs(self.system.get_all_audit_logs())
    
    def apply_filters(self):
        """
        Apply filters to the audit logs based on user input.
        """
        # Get filter values
        start_date_str = self.start_date_edit.text().strip()
        end_date_str = self.end_date_edit.text().strip()
        action = self.action_combo.text().strip()
        user = self.user_combo.text().strip()
        keyword = self.keyword_entry.text().strip()
        
        # Convert date strings to datetime objects
        start_date = None
        end_date = None
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  # End of the day
        except ValueError:
            QMessageBox.warning(self, "Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return
        
        # Adjust filter parameters
        action_filter = None if action.lower() == "all" else action
        user_filter = None if user.lower() == "all" else user
        keyword_filter = None if not keyword else keyword
        
        # Get filtered logs
        filtered_logs = self.system.filter_audit_logs(
            start_date=start_date,
            end_date=end_date,
            action=action_filter,
            user=user_filter,
            keyword=keyword_filter
        )
        
        # Display filtered logs
        self.display_logs(filtered_logs)
    
    def reset_filters(self):
        """
        Reset all filter fields and display all audit logs.
        """
        self.start_date_edit.clear()
        self.end_date_edit.clear()
        self.action_combo.clear()
        self.user_combo.clear()
        self.keyword_entry.clear()
        self.display_logs(self.system.get_all_audit_logs())
    
    def display_logs(self, logs):
        """
        Display the provided audit logs in the TreeWidget.
        """
        self.logs_tree.clear()
        for log in logs:
            item = QTreeWidgetItem([
                str(log['id']),
                log['timestamp'],
                log['user'],
                log['action'],
                log['details']
            ])
            self.logs_tree.addTopLevelItem(item)
    
    def export_logs(self):
        """
        Export the currently displayed audit logs to a CSV file.
        """
        # Gather logs from the TreeWidget
        logs = []
        for index in range(self.logs_tree.topLevelItemCount()):
            item = self.logs_tree.topLevelItem(index)
            logs.append({
                'id': item.text(0),
                'timestamp': item.text(1),
                'user': item.text(2),
                'action': item.text(3),
                'details': item.text(4)
            })
        
        if not logs:
            QMessageBox.warning(self, "No Logs", "There are no logs to export.")
            return
        
        # Ask for file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs to CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return  # User cancelled
        
        # Export logs using the mock system's method
        success, message = self.system.export_audit_logs_to_csv(logs, file_path)
        if success:
            QMessageBox.information(self, "Export Successful", message)
        else:
            QMessageBox.critical(self, "Export Failed", message)
    
    # -------------------- Audit Actions Tab --------------------
    def create_audit_actions_tab(self):
        """
        Create the 'Audit Actions' tab.
        """
        audit_actions_tab = QWidget()
        self.tabs.addTab(audit_actions_tab, "Audit Actions")
        
        # Layout for the tab
        layout = QVBoxLayout()
        audit_actions_tab.setLayout(layout)
        
        # Detailed Log Entry GroupBox
        detailed_log_group = QGroupBox("View Detailed Log Entry")
        detailed_log_layout = QFormLayout()
        detailed_log_group.setLayout(detailed_log_layout)
        layout.addWidget(detailed_log_group)
        
        # Log ID Entry
        self.log_id_entry = QLineEdit()
        self.log_id_entry.setPlaceholderText("Enter Log ID")
        detailed_log_layout.addRow(QLabel("Log ID:"), self.log_id_entry)
        
        # View Details Button
        view_details_btn = QPushButton("View Details")
        view_details_btn.clicked.connect(self.view_log_details)
        detailed_log_layout.addRow(view_details_btn)
        
        # Detailed Log Display
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Helvetica", 12))
        layout.addWidget(self.detail_text)
        
        # Generate Audit Report GroupBox
        generate_report_group = QGroupBox("Generate Audit Report")
        generate_report_layout = QHBoxLayout()
        generate_report_group.setLayout(generate_report_layout)
        layout.addWidget(generate_report_group)
        
        # Generate Report Button
        generate_report_btn = QPushButton("Generate Report")
        generate_report_btn.clicked.connect(self.generate_audit_report)
        generate_report_layout.addWidget(generate_report_btn)
        
    def view_log_details(self):
        """
        Display detailed information of a selected log entry.
        """
        log_id_str = self.log_id_entry.text().strip()
        if not log_id_str.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric Log ID.")
            return
        log_id = int(log_id_str)
        
        # Find the log entry
        log_entry = next((log for log in self.system.get_all_audit_logs() if log['id'] == log_id), None)
        if not log_entry:
            QMessageBox.warning(self, "Not Found", f"No log entry found with ID {log_id}.")
            return
        
        # Display log details
        details = (
            f"<b>Log ID:</b> {log_entry['id']}<br>"
            f"<b>Timestamp:</b> {log_entry['timestamp']}<br>"
            f"<b>User:</b> {log_entry['user']}<br>"
            f"<b>Action:</b> {log_entry['action']}<br>"
            f"<b>Details:</b> {log_entry['details']}"
        )
        self.detail_text.setHtml(details)
    
    def generate_audit_report(self):
        """
        Generate a simple audit report summary and save it as a text file.
        """
        # Generate report content
        total_logs = len(self.system.get_all_audit_logs())
        actions = {}
        for log in self.system.get_all_audit_logs():
            actions[log['action']] = actions.get(log['action'], 0) + 1
        
        report_content = f"Audit Report Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report_content += f"Total Audit Logs: {total_logs}\n\n"
        report_content += "Action Types Breakdown:\n"
        for action, count in actions.items():
            report_content += f"- {action}: {count}\n"
        
        # Ask where to save the report
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audit Report",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return  # User cancelled
        
        # Write the report to a text file
        try:
            with open(file_path, mode='w', encoding='utf-8') as report_file:
                report_file.write(report_content)
            QMessageBox.information(self, "Report Generated", f"Audit report generated successfully at '{file_path}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

# --------------------------- Main Application ---------------------------

def main():
    # Initialize the mock system
    system = MockSystem()
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Initialize the DPODashboard
    dashboard = DPODashboard(system=system)
    dashboard.show()
    
    # Execute the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
