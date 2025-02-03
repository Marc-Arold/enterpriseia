import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

# Import your real System from 'system.py'
# Adjust the path as needed, for example:
# from system import System
# or from backend.system import System
from ..system import System

# ----------------------------------------------------------------
# Example placeholder user class. Replace or remove once you have
# a real login/auth mechanism returning an authenticated user.
# ----------------------------------------------------------------
class DummyUser:
    def __init__(self, user_id=1, username="admin"):
        self.user_id = user_id
        self.username = username

    def isauthenticate(self):
        return True

# ----------------------------------------------------------------
# DPO Dashboard Class
# ----------------------------------------------------------------
class DPODashboard(QMainWindow):
    def __init__(self, system, current_user):
        super().__init__()
        self.system = system
        self.current_user = current_user
        self.setWindowTitle("DPO Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)

        self.apply_dark_theme()
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
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Title Label
        title_label = QLabel("DPO Dashboard")
        title_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.create_view_logs_tab()
        self.create_audit_actions_tab()

    # ----------------------------------------------------------------
    # 1) View Audit Logs Tab
    # ----------------------------------------------------------------
    def create_view_logs_tab(self):
        view_logs_tab = QWidget()
        self.tabs.addTab(view_logs_tab, "View Audit Logs")

        layout = QVBoxLayout()
        view_logs_tab.setLayout(layout)

        # Filters GroupBox
        filters_group = QGroupBox("Filters")
        filters_layout = QFormLayout()
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        self.start_date_edit = QLineEdit()
        self.start_date_edit.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addRow(QLabel("Start Date:"), self.start_date_edit)

        self.end_date_edit = QLineEdit()
        self.end_date_edit.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addRow(QLabel("End Date:"), self.end_date_edit)

        self.action_combo = QLineEdit()
        self.action_combo.setPlaceholderText("Enter Action Type or 'All'")
        filters_layout.addRow(QLabel("Action Type:"), self.action_combo)

        self.user_combo = QLineEdit()
        self.user_combo.setPlaceholderText("Enter User or 'All'")
        filters_layout.addRow(QLabel("User:"), self.user_combo)

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

        # TreeWidget for logs
        self.logs_tree = QTreeWidget()
        self.logs_tree.setColumnCount(5)
        self.logs_tree.setHeaderLabels(["ID", "Timestamp", "User", "Action", "Details"])
        self.logs_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.logs_tree)

        # Export Button
        export_btn = QPushButton("Export Logs to CSV")
        export_btn.clicked.connect(self.export_logs)
        layout.addWidget(export_btn, alignment=Qt.AlignRight)

        # Load logs initially
        logs = self.system.getAllAuditLogs(self.current_user)
        if isinstance(logs, list):
            # Check if user lacks permission
            if logs and isinstance(logs[0], str) and "Permission denied" in logs[0]:
                QMessageBox.warning(self, "Access Denied", logs[0])
            else:
                self.display_logs(logs)

    def apply_filters(self):
        all_logs = self.system.getAllAuditLogs(self.current_user)
        if not isinstance(all_logs, list) or (all_logs and isinstance(all_logs[0], str) and "Permission denied" in all_logs[0]):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to view logs.")
            return

        start_date_str = self.start_date_edit.text().strip()
        end_date_str = self.end_date_edit.text().strip()
        action_str = self.action_combo.text().strip()
        user_str = self.user_combo.text().strip()
        keyword_str = self.keyword_entry.text().strip()

        # Parse dates
        start_date = None
        end_date = None
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            if end_date_str:
                # End of that day
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            QMessageBox.warning(self, "Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return

        # Filter in memory
        filtered_logs = []
        for log in all_logs:
            # Convert "YYYY-MM-DD HH:MM:SS" to datetime
            log_dt = None
            if log['timestamp']:
                log_dt = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")

            if start_date and log_dt and log_dt < start_date:
                continue
            if end_date and log_dt and log_dt > end_date:
                continue
            if action_str.lower() != "all" and action_str and log['action'] != action_str:
                continue
            if user_str.lower() != "all" and user_str and log['user'] != user_str:
                continue
            if keyword_str and keyword_str.lower() not in log['details'].lower():
                continue
            filtered_logs.append(log)

        self.display_logs(filtered_logs)

    def reset_filters(self):
        self.start_date_edit.clear()
        self.end_date_edit.clear()
        self.action_combo.clear()
        self.user_combo.clear()
        self.keyword_entry.clear()

        logs = self.system.getAllAuditLogs(self.current_user)
        if isinstance(logs, list):
            if logs and isinstance(logs[0], str) and "Permission denied" in logs[0]:
                QMessageBox.warning(self, "Access Denied", logs[0])
            else:
                self.display_logs(logs)

    def display_logs(self, logs):
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
        logs = []
        for i in range(self.logs_tree.topLevelItemCount()):
            item = self.logs_tree.topLevelItem(i)
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

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs to CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return  # User cancelled

        try:
            import csv
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
            QMessageBox.information(self, "Export Successful", "Logs exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    # ----------------------------------------------------------------
    # 2) Audit Actions Tab
    # ----------------------------------------------------------------
    def create_audit_actions_tab(self):
        audit_actions_tab = QWidget()
        self.tabs.addTab(audit_actions_tab, "Audit Actions")

        layout = QVBoxLayout()
        audit_actions_tab.setLayout(layout)

        detailed_log_group = QGroupBox("View Detailed Log Entry")
        detailed_log_layout = QFormLayout()
        detailed_log_group.setLayout(detailed_log_layout)
        layout.addWidget(detailed_log_group)

        self.log_id_entry = QLineEdit()
        self.log_id_entry.setPlaceholderText("Enter Log ID")
        detailed_log_layout.addRow(QLabel("Log ID:"), self.log_id_entry)

        view_details_btn = QPushButton("View Details")
        view_details_btn.clicked.connect(self.view_log_details)
        detailed_log_layout.addRow(view_details_btn)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Helvetica", 12))
        layout.addWidget(self.detail_text)

        generate_report_group = QGroupBox("Generate Audit Report")
        generate_report_layout = QHBoxLayout()
        generate_report_group.setLayout(generate_report_layout)
        layout.addWidget(generate_report_group)

        generate_report_btn = QPushButton("Generate Report")
        generate_report_btn.clicked.connect(self.generate_audit_report)
        generate_report_layout.addWidget(generate_report_btn)

    def view_log_details(self):
        log_id_str = self.log_id_entry.text().strip()
        if not log_id_str.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric Log ID.")
            return

        log_id = int(log_id_str)
        all_logs = self.system.getAllAuditLogs(self.current_user)
        if not isinstance(all_logs, list) or (all_logs and isinstance(all_logs[0], str) and "Permission denied" in all_logs[0]):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to view logs.")
            return

        log_entry = next((l for l in all_logs if l['id'] == log_id), None)
        if not log_entry:
            QMessageBox.warning(self, "Not Found", f"No log entry found with ID {log_id}.")
            return

        details = (
            f"<b>Log ID:</b> {log_entry['id']}<br>"
            f"<b>Timestamp:</b> {log_entry['timestamp']}<br>"
            f"<b>User:</b> {log_entry['user']}<br>"
            f"<b>Action:</b> {log_entry['action']}<br>"
            f"<b>Details:</b> {log_entry['details']}"
        )
        self.detail_text.setHtml(details)

    def generate_audit_report(self):
        all_logs = self.system.getAllAuditLogs(self.current_user)
        if not isinstance(all_logs, list) or (all_logs and isinstance(all_logs[0], str) and "Permission denied" in all_logs[0]):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to view logs.")
            return

        total_logs = len(all_logs)
        actions_count = {}
        for log in all_logs:
            actions_count[log['action']] = actions_count.get(log['action'], 0) + 1

        report_content = f"Audit Report Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report_content += f"Total Audit Logs: {total_logs}\n\n"
        report_content += "Action Types Breakdown:\n"
        for action, count in actions_count.items():
            report_content += f"- {action}: {count}\n"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audit Report",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, mode='w', encoding='utf-8') as report_file:
                report_file.write(report_content)
            QMessageBox.information(self, "Report Generated", f"Audit report generated at '{file_path}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main():
    app = QApplication(sys.argv)

    # Instantiate your real System (from system.py) with any needed parameters
    real_system = System(
        # external_api_key="YOUR_EXTERNAL_API_KEY",
        # retention_days=90
    )

    # Example user object with admin-like privileges. Replace with your real user from a login system.
    current_user = DummyUser()

    dashboard = DPODashboard(system=real_system, current_user=current_user)
    dashboard.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
