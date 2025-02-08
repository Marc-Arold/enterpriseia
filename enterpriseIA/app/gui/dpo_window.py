import sys
from datetime import datetime, timedelta, time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QGroupBox, QFormLayout,
    QDateEdit, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPalette, QColor, QIcon

# Import your real System from 'system.py'
from ..system import System

# ----------------------------------------------------------------
# Placeholder user class. Replace or remove once you have a real
# login/auth mechanism returning an authenticated user.
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
        # Set the window icon using the helper method to compute its absolute path
        self.setWindowIcon(self._get_icon("app_icon"))

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
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
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

        # Top header layout with title on the left and the button on the right
        header_layout = QHBoxLayout()
        title_label = QLabel("DPO Dashboard")
        title_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        # --- New Button in Top Right to Redirect to Chat Interface ---
        go_to_chat_btn = QPushButton("Go to Chat Interface")
        go_to_chat_btn.setToolTip("Redirect to the Chat Interface")
        go_to_chat_btn.clicked.connect(self.open_chat_interface)
        header_layout.addWidget(go_to_chat_btn)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(10)

        # Create Tabs
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

        # Date Filter Checkbox and QDateEdits
        self.date_filter_checkbox = QCheckBox("Filter by Date")
        self.date_filter_checkbox.setToolTip("Check to enable date filtering")
        self.date_filter_checkbox.stateChanged.connect(self.toggle_date_filters)
        filters_layout.addRow(self.date_filter_checkbox)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setToolTip("Select the start date for filtering")
        self.start_date_edit.setEnabled(False)
        filters_layout.addRow(QLabel("Start Date:"), self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setToolTip("Select the end date for filtering")
        self.end_date_edit.setEnabled(False)
        filters_layout.addRow(QLabel("End Date:"), self.end_date_edit)

        # Action Type Filter using QComboBox
        self.action_combo = QComboBox()
        self.action_combo.addItem("All")
        # Optionally populate with specific actions:
        # self.action_combo.addItems(self.system.getAvailableActions())
        self.action_combo.setToolTip("Select an action type to filter, or choose 'All'")
        filters_layout.addRow(QLabel("Action Type:"), self.action_combo)

        # User Filter using QComboBox
        self.user_combo = QComboBox()
        self.user_combo.addItem("All")
        # Optionally populate with specific users:
        # self.user_combo.addItems(self.system.getAvailableUsers())
        self.user_combo.setToolTip("Select a user to filter, or choose 'All'")
        filters_layout.addRow(QLabel("User:"), self.user_combo)

        # Keyword filter using QLineEdit
        self.keyword_entry = QLineEdit()
        self.keyword_entry.setPlaceholderText("Enter Keyword")
        self.keyword_entry.setToolTip("Type a keyword to search within log details")
        filters_layout.addRow(QLabel("Keyword:"), self.keyword_entry)

        # Filter Buttons
        buttons_layout = QHBoxLayout()
        apply_filter_btn = QPushButton("Apply Filters")
        apply_filter_btn.setToolTip("Apply selected filters")
        apply_filter_btn.clicked.connect(self.apply_filters)
        reset_filter_btn = QPushButton("Reset Filters")
        reset_filter_btn.setToolTip("Reset all filters to default")
        reset_filter_btn.clicked.connect(self.reset_filters)
        buttons_layout.addWidget(apply_filter_btn)
        buttons_layout.addWidget(reset_filter_btn)
        layout.addLayout(buttons_layout)
        layout.addSpacing(10)

        # Logs TreeWidget
        self.logs_tree = QTreeWidget()
        self.logs_tree.setColumnCount(5)
        self.logs_tree.setHeaderLabels(["ID", "Timestamp", "User", "Action", "Details"])
        self.logs_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_tree.setToolTip("Double-click a log entry for detailed view")
        self.logs_tree.itemDoubleClicked.connect(self.log_item_double_clicked)
        layout.addWidget(self.logs_tree)

        # Export Button
        export_btn = QPushButton("Export Logs to CSV")
        export_btn.setToolTip("Export current logs view to a CSV file")
        export_btn.clicked.connect(self.export_logs)
        layout.addWidget(export_btn, alignment=Qt.AlignRight)

        # Initial load of logs
        logs = self.system.getAllAuditLogs(self.current_user)
        if isinstance(logs, list):
            if logs and isinstance(logs[0], str) and "Permission denied" in logs[0]:
                QMessageBox.warning(self, "Access Denied", logs[0])
            else:
                self.display_logs(logs)

    def toggle_date_filters(self, state):
        enabled = state == Qt.Checked
        self.start_date_edit.setEnabled(enabled)
        self.end_date_edit.setEnabled(enabled)

    def apply_filters(self):
        all_logs = self.system.getAllAuditLogs(self.current_user)
        if not isinstance(all_logs, list) or (all_logs and isinstance(all_logs[0], str) and "Permission denied" in all_logs[0]):
            QMessageBox.warning(self, "Access Denied", "You do not have permission to view logs.")
            return

        # Date filtering: only if checkbox is checked
        start_date = None
        end_date = None
        if self.date_filter_checkbox.isChecked():
            start_qdate = self.start_date_edit.date()
            end_qdate = self.end_date_edit.date()
            start_date = datetime(start_qdate.year(), start_qdate.month(), start_qdate.day(), 0, 0, 0)
            end_date = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day(), 23, 59, 59)

        action_filter = self.action_combo.currentText().strip().lower()
        user_filter = self.user_combo.currentText().strip().lower()
        keyword_filter = self.keyword_entry.text().strip().lower()

        filtered_logs = []
        for log in all_logs:
            try:
                log_dt = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue

            if start_date and log_dt < start_date:
                continue
            if end_date and log_dt > end_date:
                continue
            if action_filter != "all" and log['action'].lower() != action_filter:
                continue
            if user_filter != "all" and log['user'].lower() != user_filter:
                continue
            if keyword_filter and keyword_filter not in log['details'].lower():
                continue

            filtered_logs.append(log)

        self.display_logs(filtered_logs)

    def reset_filters(self):
        self.date_filter_checkbox.setChecked(False)
        today = QDate.currentDate()
        self.start_date_edit.setDate(today)
        self.end_date_edit.setDate(today)
        self.action_combo.setCurrentIndex(0)
        self.user_combo.setCurrentIndex(0)
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

    def log_item_double_clicked(self, item, column):
        details = (
            f"<b>Log ID:</b> {item.text(0)}<br>"
            f"<b>Timestamp:</b> {item.text(1)}<br>"
            f"<b>User:</b> {item.text(2)}<br>"
            f"<b>Action:</b> {item.text(3)}<br>"
            f"<b>Details:</b> {item.text(4)}"
        )
        QMessageBox.information(self, "Log Details", details)

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
            return

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

        # Detailed Log Entry Group
        detailed_log_group = QGroupBox("View Detailed Log Entry")
        detailed_log_layout = QFormLayout()
        detailed_log_group.setLayout(detailed_log_layout)
        layout.addWidget(detailed_log_group)

        self.log_id_entry = QLineEdit()
        self.log_id_entry.setPlaceholderText("Enter Log ID")
        self.log_id_entry.setToolTip("Type the Log ID you wish to view")
        detailed_log_layout.addRow(QLabel("Log ID:"), self.log_id_entry)

        view_details_btn = QPushButton("View Details")
        view_details_btn.setToolTip("Click to view details for the specified Log ID")
        view_details_btn.clicked.connect(self.view_log_details)
        detailed_log_layout.addRow(view_details_btn)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Helvetica", 12))
        self.detail_text.setToolTip("Detailed log information will be displayed here")
        layout.addWidget(self.detail_text)
        layout.addSpacing(10)

        # Generate Audit Report Group
        generate_report_group = QGroupBox("Generate Audit Report")
        generate_report_layout = QHBoxLayout()
        generate_report_group.setLayout(generate_report_layout)
        layout.addWidget(generate_report_group)

        generate_report_btn = QPushButton("Generate Report")
        generate_report_btn.setToolTip("Generate an audit report based on available logs")
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
    # New Method: Redirect to Chat Interface
    # ----------------------------------------------------------------
    def open_chat_interface(self):
        # Redirect: Close the current dashboard and open the chat interface in its place
        from employee_window import EmployeeChatDashboard
        self.chat_interface = EmployeeChatDashboard(system=self.system, user=self.current_user)
        self.chat_interface.show()
        self.close()

    # ----------------------------------------------------------------
    # Helper Method for Icons
    # ----------------------------------------------------------------
    def _get_icon(self, name: str) -> QIcon:
        """
        Compute the absolute path for the icon relative to this file
        and return a QIcon object.
        """
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{name}.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon.fromTheme(name)

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

    # Example user object. Replace with your real user from a login system.
    current_user = DummyUser()

    dashboard = DPODashboard(system=real_system, current_user=current_user)
    dashboard.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
