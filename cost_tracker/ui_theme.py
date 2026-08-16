"""Fusion stylesheet for a readable desktop layout."""

APP_STYLESHEET = """
QMainWindow, QDialog {
    background: #f4f6f8;
    color: #1f2933;
}
QWidget {
    font-size: 13px;
}
QLabel#title {
    font-size: 22px;
    font-weight: 600;
}
QLabel#subtitle {
    color: #52606d;
}
QLabel#monthTitle {
    font-size: 18px;
    font-weight: 600;
}
QPushButton {
    padding: 7px 14px;
    border: 1px solid #cbd2d9;
    border-radius: 6px;
    background: #ffffff;
}
QPushButton:hover {
    background: #eef2f6;
}
QPushButton:disabled {
    color: #9aa5b1;
}
QPushButton[cssClass="primary"] {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
}
QPushButton[cssClass="primary"]:hover {
    background: #1d4ed8;
}
QLineEdit, QTableWidget {
    background: #ffffff;
    border: 1px solid #cbd2d9;
    border-radius: 4px;
}
QTableWidget {
    gridline-color: #e4e7eb;
    selection-background-color: #dbeafe;
    selection-color: #1f2933;
}
QHeaderView::section {
    background: #e4e7eb;
    padding: 4px;
    border: none;
    font-weight: 600;
}
QFrame#summaryCard {
    background: #ffffff;
    border: 1px solid #d9e2ec;
    border-radius: 8px;
}
"""
